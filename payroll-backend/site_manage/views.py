"""
site_manage/views.py — Payroll domain views.

Auth, registration, company, subscription, and config views have moved to users/views.py.

ViewSets:
  - ProviderViewSet       → /providers/
  - PayrollViewSet        → /payrolls/
  - DashboardView         → /dashboard/
  - generate_receipt      → /receipt/<pk>/
"""

from datetime import datetime, timedelta

from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment, Provider, Payroll
from .permissions import IsCustomerAdminOrReadOnly
from .selectors import (
    dashboard_stats_for_company,
    payroll_list_for_user,
    provider_list_for_user,
    subscription_can_add_provider,
)
from .serializers import (
    PayrollDetailSerializer,
    PayrollSerializer,
    ProviderSerializer,
)
from services.payroll_service import PayrollService
from services.email_service import EmailService


# ==============================================================================
# PROVIDERS
# ==============================================================================


class ProviderViewSet(viewsets.ModelViewSet):
    """
    ViewSet protegido para gerenciar Providers com multi-tenancy.

    Permissions:
    - Customer Admin: pode criar, editar e deletar providers da sua empresa
    - Provider: pode apenas visualizar seu próprio perfil
    - Super Admin: acesso total (todas as empresas)

    Routes:
      GET    /providers/           → list
      POST   /providers/           → create
      GET    /providers/{id}/      → retrieve
      PUT    /providers/{id}/      → update
      PATCH  /providers/{id}/      → partial_update
      DELETE /providers/{id}/      → destroy
    """

    queryset = Provider.objects.all()  # Necessário para o router
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["role", "payment_method"]
    ordering_fields = ["name", "monthly_value", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Filtrar providers por empresa do usuário via selector."""
        return provider_list_for_user(user=self.request.user).order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_create(serializer)
        except Exception as e:
            from rest_framework.exceptions import ValidationError

            if isinstance(e, ValidationError):
                # DRF ValidationError can be a list or dict. Normalize to detail for frontend.
                msg = (
                    e.detail[0]
                    if isinstance(e.detail, list) and e.detail
                    else str(e.detail)
                )
                return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)
            raise e

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        """Ao criar provider, associar à empresa do Customer Admin."""
        if self.request.user.role == "CUSTOMER_ADMIN":
            company = self.request.user.company

            if not subscription_can_add_provider(company=company):
                from rest_framework.exceptions import ValidationError

                raise ValidationError(
                    "Limite de prestadores atingido. "
                    "Faça o upgrade do seu plano para adicionar mais prestadores."
                )

            serializer.save(company=company)
        else:
            serializer.save()


# ==============================================================================
# PAYROLLS
# ==============================================================================


class PayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet protegido para gerenciar Payrolls com multi-tenancy.

    Permissions:
    - Customer Admin: pode gerenciar payrolls dos providers da sua empresa
    - Provider: pode apenas visualizar seus próprios payrolls
    - Super Admin: acesso total

    Routes:
      GET    /payrolls/                      → list
      GET    /payrolls/{id}/                 → retrieve
      PUT    /payrolls/{id}/                 → update
      PATCH  /payrolls/{id}/                 → partial_update
      DELETE /payrolls/{id}/                 → destroy
      POST   /payrolls/calculate/            → calculate (criar + calcular)
      POST   /payrolls/{id}/close/           → close_payroll
      POST   /payrolls/{id}/mark-as-paid/    → mark_as_paid
      POST   /payrolls/{id}/reopen/          → reopen_payroll
      GET    /payrolls/{id}/export-file/     → export_file (.xlsx)
      GET    /payrolls/monthly-report/       → monthly_report (.csv)
      POST   /payrolls/email-report/         → email_report
      GET    /payrolls/stats/                → stats
    """

    queryset = Payroll.objects.all()  # Necessário para o router
    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "reference_month", "provider"]
    ordering_fields = ["reference_month", "created_at", "net_value"]
    ordering = ["-reference_month", "provider__name"]

    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na action."""
        if self.action == "retrieve":
            return PayrollDetailSerializer
        if self.action in ["update", "partial_update"]:
            from .serializers import PayrollUpdateSerializer

            return PayrollUpdateSerializer
        return PayrollSerializer

    def get_queryset(self):
        """Filtrar payrolls por empresa do usuário via selector."""
        return payroll_list_for_user(user=self.request.user)

    def perform_update(self, serializer):
        """Sobrescreve o update padrão para usar o PayrollService e recalcular valores."""
        service = PayrollService()
        service.recalculate_payroll(serializer.instance.id, **serializer.validated_data)

    def update(self, request, *args, **kwargs):
        """
        Sobrescreve update para retornar o objeto completo serializado,
        não apenas os campos editados (já que PayrollUpdateSerializer é limitado).
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance.refresh_from_db()
        read_serializer = PayrollDetailSerializer(instance)
        return Response(read_serializer.data)

    # ── Actions ────────────────────────────────────────────────────────────────

    @action(detail=False, methods=["post"], url_path="calculate")
    def calculate(self, request):
        """
        Cria e calcula uma nova folha de pagamento via PayrollService.

        POST /payrolls/calculate/
        """
        from .serializers import PayrollCreateSerializer

        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode criar folhas de pagamento."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PayrollCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider_id = serializer.validated_data["provider_id"]

        try:
            provider = Provider.objects.get(id=provider_id)
            if provider.company != request.user.company:
                return Response(
                    {
                        "error": "Você não tem permissão para criar folha para este prestador."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Provider.DoesNotExist:
            return Response(
                {"error": "Prestador não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            service = PayrollService()
            payroll = service.create_payroll(
                provider_id=provider_id,
                reference_month=serializer.validated_data["reference_month"],
                overtime_hours_50=serializer.validated_data.get("overtime_hours_50", 0),
                holiday_hours=serializer.validated_data.get("holiday_hours", 0),
                night_hours=serializer.validated_data.get("night_hours", 0),
                late_minutes=serializer.validated_data.get("late_minutes", 0),
                absence_days=serializer.validated_data.get("absence_days", 0),
                absence_hours=serializer.validated_data.get("absence_hours", 0),
                manual_discounts=serializer.validated_data.get("manual_discounts", 0),
                notes=serializer.validated_data.get("notes", ""),
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="close")
    def close_payroll(self, request, pk=None):
        """
        Fecha uma folha de pagamento (DRAFT → CLOSED) via PayrollService.

        POST /payrolls/{id}/close/
        """
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode fechar folhas de pagamento."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payroll = self.get_object()

        if payroll.provider.company != request.user.company:
            return Response(
                {"error": "Você não tem permissão para fechar esta folha."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = PayrollService().close_payroll(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="mark-as-paid")
    def mark_as_paid(self, request, pk=None):
        """
        Marca uma folha como paga (CLOSED → PAID) via PayrollService.

        POST /payrolls/{id}/mark-as-paid/
        """
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode marcar folhas como pagas."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payroll = self.get_object()

        if payroll.provider.company != request.user.company:
            return Response(
                {"error": "Você não tem permissão para atualizar esta folha."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = PayrollService().mark_as_paid(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="reopen")
    def reopen_payroll(self, request, pk=None):
        """
        Reabre uma folha fechada (CLOSED → DRAFT) via PayrollService.

        POST /payrolls/{id}/reopen/
        """
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode reabrir folhas de pagamento."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payroll = self.get_object()

        if payroll.provider.company != request.user.company:
            return Response(
                {"error": "Você não tem permissão para reabrir esta folha."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = PayrollService().reopen_payroll(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], url_path="export-file")
    def export_file(self, request, pk=None):
        """
        Exporta a folha de pagamento em formato de planilha (.xlsx).

        GET /payrolls/{id}/export-file/
        """
        from services.excel_service import ExcelService
        from django.http import Http404

        try:
            payroll = self.get_object()
            excel_service = ExcelService()
            file_content = excel_service.generate_payroll_excel(payroll)
            filename = excel_service.get_filename(payroll)

            response = HttpResponse(
                file_content.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        except Http404:
            raise
        except Exception as e:
            return Response(
                {"error": f"Erro ao gerar arquivo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="monthly-report")
    def monthly_report(self, request):
        """
        Gera um relatório CSV consolidado para um mês específico.

        GET /payrolls/monthly-report/?reference_month=MM/YYYY
        """
        from services.report_service import ReportService

        reference_month = request.query_params.get("reference_month")

        if not reference_month:
            return Response(
                {"error": "Parâmetro reference_month é obrigatório (formato MM/YYYY)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode gerar relatórios mensais."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            file_content = ReportService().generate_monthly_summary(
                company_id=request.user.company.id, reference_month=reference_month
            )
            filename = f"relatorio_mensal_{reference_month.replace('/', '-')}.csv"
            response = HttpResponse(
                file_content.getvalue(), content_type="text/csv; charset=utf-8"
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            return Response(
                {"error": f"Erro ao gerar relatório: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="email-report")
    def email_report(self, request):
        """
        Gera e envia por e-mail um relatório mensal.

        POST /payrolls/email-report/
        Body: { "reference_month": "MM/YYYY", "email": "optional@email.com" }
        """
        from services.report_service import ReportService

        reference_month = request.data.get("reference_month")
        email_address = request.data.get("email") or request.user.email

        if not reference_month:
            return Response(
                {"error": "Parâmetro reference_month é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not email_address:
            return Response(
                {
                    "error": "E-mail não fornecido e usuário não possui e-mail cadastrado."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode enviar relatórios."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            file_content = ReportService().generate_monthly_summary(
                company_id=request.user.company.id, reference_month=reference_month
            )
            filename = f"relatorio_mensal_{reference_month.replace('/', '-')}.csv"

            success = EmailService().send_report_email(
                recipient_email=email_address,
                subject=f"Relatorio Mensal de Folha de Pagamento - {reference_month}",
                body=(
                    f"Prezado(a),\n\nSegue em anexo o relatorio mensal consolidado "
                    f"referente ao mes {reference_month}.\n\nAtenciosamente,\nSistema de Folha de Pagamento"
                ),
                attachment_name=filename,
                attachment_content=file_content.getvalue(),
                content_type="text/csv",
            )

            if success:
                return Response(
                    {"message": f"Relatório enviado com sucesso para {email_address}!"}
                )
            else:
                return Response(
                    {"error": "Falha ao enviar e-mail. Verifique os logs do sistema."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            return Response(
                {"error": f"Erro ao processar solicitação: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """
        Retorna estatísticas gerais de payrolls (independente de filtros de paginação).

        GET /payrolls/stats/
        """
        queryset = self.get_queryset()
        return Response(
            {
                "total": queryset.count(),
                "draft": queryset.filter(status="DRAFT").count(),
                "paid": queryset.filter(status="PAID").count(),
            }
        )


# ==============================================================================
# DASHBOARD
# ==============================================================================


class DashboardView(APIView):
    """
    Dashboard protegido — apenas Customer Admin pode acessar.
    Delega as queries ao selector dashboard_stats_for_company().

    GET /dashboard/
    GET /dashboard/?period=7d|30d|90d|1y|all
    GET /dashboard/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "CUSTOMER_ADMIN":
            return Response(
                {
                    "error": "Acesso negado. Apenas Customer Admin pode acessar o dashboard."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Parse period filters
        period = request.GET.get("period", "30d")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            end = datetime.now().date()
            period_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
            days = period_map.get(period)
            start = (end - timedelta(days=days)) if days else None

        # Calcular meses no período
        months_in_range = None
        if start:
            from dateutil.relativedelta import relativedelta

            months_in_range = []
            current = start.replace(day=1)
            end_month = end.replace(day=1)
            while current <= end_month:
                months_in_range.append(current.strftime("%m/%Y"))
                current = current + relativedelta(months=1)

        # Stats via selector
        stats = dashboard_stats_for_company(company=user.company)

        # Agregação mensal
        from django.db.models import Count, Sum
        from decimal import Decimal

        company_payrolls = Payroll.objects.filter(provider__company=user.company)
        if months_in_range:
            company_payrolls = company_payrolls.filter(
                reference_month__in=months_in_range
            )

        monthly_aggregated = (
            company_payrolls.values("reference_month", "status")
            .annotate(count=Count("id"), total_value=Sum("net_value"))
            .order_by("reference_month", "status")
        )

        monthly_data = {}
        for item in monthly_aggregated:
            month = item["reference_month"]
            item_status = item["status"].lower()

            if month not in monthly_data:
                monthly_data[month] = {
                    "draft": {"count": 0, "value": 0},
                    "closed": {"count": 0, "value": 0},
                    "paid": {"count": 0, "value": 0},
                    "total_count": 0,
                    "total_value": 0,
                    "avg_value": 0,
                }

            monthly_data[month][item_status] = {
                "count": item["count"],
                "value": float(item["total_value"] or Decimal("0")),
            }
            monthly_data[month]["total_count"] += item["count"]
            monthly_data[month]["total_value"] += float(
                item["total_value"] or Decimal("0")
            )

        for month in monthly_data:
            count = monthly_data[month]["total_count"]
            if count > 0:
                monthly_data[month]["avg_value"] = (
                    monthly_data[month]["total_value"] / count
                )

        # Tendências
        trends = {
            "monthly_growth_percentage": 0,
            "period_vs_previous": {
                "payrolls_change": 0,
                "value_change": 0,
            },
        }
        sorted_months = sorted(
            monthly_data.keys(), key=lambda x: (x.split("/")[1], x.split("/")[0])
        )
        if len(sorted_months) >= 2:
            last_month = sorted_months[-1]
            prev_month = sorted_months[-2]
            last_total = sum(
                monthly_data[last_month][s]["value"]
                for s in ["draft", "closed", "paid"]
            )
            prev_total = sum(
                monthly_data[prev_month][s]["value"]
                for s in ["draft", "closed", "paid"]
            )
            last_count = monthly_data[last_month]["total_count"]
            prev_count = monthly_data[prev_month]["total_count"]
            if prev_total > 0:
                trends["monthly_growth_percentage"] = (
                    (last_total - prev_total) / prev_total
                ) * 100
                trends["period_vs_previous"]["value_change"] = (
                    (last_total - prev_total) / prev_total
                ) * 100
            if prev_count > 0:
                trends["period_vs_previous"]["payrolls_change"] = (
                    (last_count - prev_count) / prev_count
                ) * 100

        # Atividade recente
        recent_payrolls = company_payrolls.select_related("provider").order_by(
            "-created_at"
        )[:10]

        return Response(
            {
                "stats": stats,
                "monthly_aggregation": monthly_data,
                "trends": trends,
                "recent_activity": PayrollSerializer(recent_payrolls, many=True).data,
            }
        )


# ==============================================================================
# RECEIPT
# ==============================================================================


def generate_receipt(request, pk):
    """
    Simple Text Receipt for MVP.
    Kept for legacy compatibility — generates a plain-text receipt for payments.

    GET /receipt/<pk>/
    """
    try:
        payment = Payment.objects.get(pk=pk)
        content = f"""
        RECIBO DE PAGAMENTO
        -------------------
        Prestador: {payment.provider.name}
        Referência: {payment.reference}
        Valor: R$ {payment.total_calculated}
        Data: {payment.paid_at}
        Status: {payment.status}
        -------------------
        Gerado pelo Payroll System
        """
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="recibo_{pk}.txt"'
        return response
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)
