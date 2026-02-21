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
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from site_manage.api.serializers import (
    PayrollCreateSerializer,
    PayrollDetailSerializer,
    PayrollSerializer,
    PayrollUpdateSerializer,
    ProviderSerializer,
)
from site_manage.application.commands.email_service import EmailService
from site_manage.application.commands.payroll_service import PayrollService
from site_manage.application.queries.selectors import (
    dashboard_stats_for_company,
    payroll_list_for_user,
    provider_list_for_user,
)
from site_manage.infrastructure.models import Payment, Payroll, Provider
from site_manage.permissions import IsCustomerAdminOrReadOnly
from users.application.queries.selectors import subscription_can_add_provider

# ==============================================================================
# PROVIDERS
# ==============================================================================


class ProviderListCreateAPIView(APIView):
    """
    Lista Providers do tenant ou cria novo.

    GET /providers/
    POST /providers/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        # Seleciona de acordo com tenant/user rules
        providers = provider_list_for_user(user=request.user).order_by("name")

        # Filtros manuais básicos compatíveis com DjangoFilterBackend legados
        role_filter = request.query_params.get("role")
        if role_filter:
            providers = providers.filter(role=role_filter)

        payment_method_filter = request.query_params.get("payment_method")
        if payment_method_filter:
            providers = providers.filter(payment_method=payment_method_filter)

        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ProviderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Associa à empresa do Admin
        if request.user.role == "CUSTOMER_ADMIN":
            company = request.user.company
            if not subscription_can_add_provider(company=company):
                return Response(
                    {
                        "detail": "Limite de prestadores atingido. Faça o upgrade do seu plano para complementar."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save(company=company)
        else:
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProviderDetailAPIView(APIView):
    """
    Consulta, Atualiza ou Exclui um Provider específico.

    GET /providers/{id}/
    PUT /providers/{id}/
    PATCH /providers/{id}/
    DELETE /providers/{id}/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get_object(self, request, pk):
        try:
            # Garante tenant isolation
            provider = provider_list_for_user(user=request.user).get(pk=pk)
            return provider
        except Provider.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        provider = self.get_object(request, pk)
        if not provider:
            return Response(
                {"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProviderSerializer(provider)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        provider = self.get_object(request, pk)
        if not provider:
            return Response(
                {"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProviderSerializer(provider, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        provider = self.get_object(request, pk)
        if not provider:
            return Response(
                {"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProviderSerializer(provider, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        provider = self.get_object(request, pk)
        if not provider:
            return Response(
                {"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        provider.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# PAYROLLS
# ==============================================================================


class PayrollListAPIView(APIView):
    """
    Lista de Payrolls do tenant.
    GET /payrolls/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        payrolls = payroll_list_for_user(user=request.user).order_by(
            "-reference_month", "provider__name"
        )

        # Filtros manuais básicos compensando DjangoFilterBackend
        status_filter = request.query_params.get("status")
        if status_filter:
            payrolls = payrolls.filter(status=status_filter)

        ref_month_filter = request.query_params.get("reference_month")
        if ref_month_filter:
            payrolls = payrolls.filter(reference_month=ref_month_filter)

        provider_filter = request.query_params.get("provider")
        if provider_filter:
            payrolls = payrolls.filter(provider_id=provider_filter)

        serializer = PayrollSerializer(payrolls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PayrollDetailAPIView(APIView):
    """
    Consulta ou atualiza os detalhes de Payout usando Serializers limitados ou serviços de refatoração.
    GET /payrolls/{id}/
    PUT /payrolls/{id}/
    PATCH /payrolls/{id}/
    DELETE /payrolls/{id}/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get_object(self, request, pk):
        from django.http import Http404

        try:
            return payroll_list_for_user(user=request.user).get(pk=pk)
        except Payroll.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        payroll = self.get_object(request, pk)
        serializer = PayrollDetailSerializer(payroll)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, instance, validated_data):
        service = PayrollService()
        service.recalculate_payroll(instance.id, **validated_data)

    def put(self, request, pk, *args, **kwargs):
        return self._update(request, pk, partial=False)

    def patch(self, request, pk, *args, **kwargs):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        instance = self.get_object(request, pk)
        serializer = PayrollUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            self.perform_update(instance, serializer.validated_data)
            instance.refresh_from_db()
            return Response(
                PayrollDetailSerializer(instance).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        instance = self.get_object(request, pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PayrollCalculateAPIView(APIView):
    """
    Cria e calcula nova folha.
    POST /payrolls/calculate/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode criar folhas de pagamento."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PayrollCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            payroll = PayrollService().create_payroll(
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


class PayrollCloseAPIView(APIView):
    """
    Fecha a folha. (DRAFT → CLOSED)
    POST /payrolls/{id}/close/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, pk, *args, **kwargs):
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode fechar folhas."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = payroll_list_for_user(user=request.user).get(pk=pk)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        if payroll.provider.company != request.user.company:
            return Response(
                {"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            payroll = PayrollService().close_payroll(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )


class PayrollMarkPaidAPIView(APIView):
    """
    Marca como paga. (CLOSED → PAID)
    POST /payrolls/{id}/mark-as-paid/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, pk, *args, **kwargs):
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode marcar como paga."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = payroll_list_for_user(user=request.user).get(pk=pk)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            payroll = PayrollService().mark_as_paid(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )


class PayrollReopenAPIView(APIView):
    """
    Reabre folha fechada. (CLOSED → DRAFT)
    POST /payrolls/{id}/reopen/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, pk, *args, **kwargs):
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode reabrir."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = payroll_list_for_user(user=request.user).get(pk=pk)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            payroll = PayrollService().reopen_payroll(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )


class PayrollExportFileAPIView(APIView):
    """
    Exporta ficheiro Excel.
    GET /payrolls/{id}/export-file/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, pk, *args, **kwargs):
        from site_manage.application.commands.excel_service import ExcelService

        try:
            payroll = payroll_list_for_user(user=request.user).get(pk=pk)
            excel_service = ExcelService()
            file_content = excel_service.generate_payroll_excel(payroll)
            filename = excel_service.get_filename(payroll)

            response = HttpResponse(
                file_content.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PayrollMonthlyReportAPIView(APIView):
    """
    Relatório mensal em CSV.
    GET /payrolls/monthly-report/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        from site_manage.application.commands.report_service import ReportService

        reference_month = request.query_params.get("reference_month")

        if not reference_month:
            return Response(
                {"error": "Parâmetro reference_month é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin."}, status=status.HTTP_403_FORBIDDEN
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
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PayrollEmailReportAPIView(APIView):
    """
    Envia relatório por email.
    POST /payrolls/email-report/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        from site_manage.application.commands.report_service import ReportService

        reference_month = request.data.get("reference_month")
        email_address = request.data.get("email") or request.user.email

        if not reference_month or not email_address:
            return Response(
                {"error": "Mes e email necessarios."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin."}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            file_content = ReportService().generate_monthly_summary(
                company_id=request.user.company.id, reference_month=reference_month
            )
            filename = f"relatorio_mensal_{reference_month.replace('/', '-')}.csv"

            success = EmailService().send_report_email(
                recipient_email=email_address,
                subject=f"Relatorio Folha - {reference_month}",
                body="Em anexo o relatorio.",
                attachment_name=filename,
                attachment_content=file_content.getvalue(),
                content_type="text/csv",
            )
            if success:
                return Response({"message": f"Enviado para {email_address}!"})
            return Response(
                {"error": "Falha ao enviar."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PayrollStatsAPIView(APIView):
    """
    Stats de status das folhas.
    GET /payrolls/stats/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        queryset = payroll_list_for_user(user=request.user)
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
        stats = dashboard_stats_for_company(company_id=user.company.id)

        # Agregação mensal
        from decimal import Decimal

        from django.db.models import Count, Sum

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
