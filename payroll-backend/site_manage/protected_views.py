"""
Protected ViewSets with Company Scoping and Role-Based Permissions

Este arquivo contém as versões atualizadas dos ViewSets com:
- Filtros por empresa (multi-tenancy)
- Permissões baseadas em roles
- Proteção de endpoints

Para usar: substituir os ViewSets correspondentes em views.py
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Provider, Payroll
from .serializers import ProviderSerializer, PayrollSerializer, PayrollDetailSerializer
from .permissions import IsCustomerAdminOrReadOnly, customer_admin_only


class ProtectedProviderViewSet(viewsets.ModelViewSet):
    """
    ViewSet protegido para gerenciar Providers com multi-tenancy.

    Permissions:
    - Customer Admin: pode criar, editar e deletar providers da sua empresa
    - Provider: pode apenas visualizar seu próprio perfil
    - Super Admin: acesso total (todas as empresas)
    """

    queryset = Provider.objects.all()  # Necessário para o router
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["role", "payment_method"]
    ordering_fields = ["name", "monthly_value", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Filtrar providers por empresa do usuário"""
        user = self.request.user

        if user.role == "SUPER_ADMIN":
            return Provider.objects.all().order_by("name")
        elif user.role == "CUSTOMER_ADMIN":
            return Provider.objects.filter(company=user.company).order_by("name")
        elif user.role == "PROVIDER":
            if hasattr(user, "provider_profile"):
                return Provider.objects.filter(id=user.provider_profile.id)
            return Provider.objects.none()

        return Provider.objects.none()

    def perform_create(self, serializer):
        """Ao criar provider, associar à empresa do Customer Admin"""
        if self.request.user.role == "CUSTOMER_ADMIN":
            serializer.save(company=self.request.user.company)
        else:
            serializer.save()


class ProtectedPayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet protegido para gerenciar Payrolls com multi-tenancy.

    Permissions:
    - Customer Admin: pode gerenciar payrolls dos providers da sua empresa
    - Provider: pode apenas visualizar seus próprios payrolls
    - Super Admin: acesso total
    """

    queryset = Payroll.objects.all()  # Necessário para o router
    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "reference_month", "provider"]
    ordering_fields = ["reference_month", "created_at", "net_value"]
    ordering = ["-reference_month", "provider__name"]

    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na action"""
        if self.action == "retrieve":
            return PayrollDetailSerializer
        return PayrollSerializer

    def get_queryset(self):
        """Filtrar payrolls por empresa do usuário"""
        user = self.request.user

        if user.role == "SUPER_ADMIN":
            return (
                Payroll.objects.all()
                .select_related("provider")
                .prefetch_related("items")
            )
        elif user.role == "CUSTOMER_ADMIN":
            # Customer Admin vê payrolls dos providers da sua empresa
            return (
                Payroll.objects.filter(provider__company=user.company)
                .select_related("provider")
                .prefetch_related("items")
            )
        elif user.role == "PROVIDER":
            # Provider vê apenas seus próprios payrolls
            if hasattr(user, "provider_profile"):
                return (
                    Payroll.objects.filter(provider=user.provider_profile)
                    .select_related("provider")
                    .prefetch_related("items")
                )
            return Payroll.objects.none()

        return Payroll.objects.none()

    @action(detail=True, methods=["get"], url_path="export-excel")
    def export_excel(self, request, pk=None):
        """
        Exporta a folha de pagamento em formato Excel (.xlsx).

        GET /payrolls/{id}/export-excel/

        Returns:
            Arquivo Excel formatado com todos os detalhes da folha
        """
        from services.excel_service import ExcelService
        from django.http import Http404, HttpResponse

        try:
            payroll = self.get_object()

            # Gerar arquivo Excel
            excel_service = ExcelService()
            excel_file = excel_service.generate_payroll_excel(payroll)
            filename = excel_service.get_filename(payroll)

            # Criar resposta HTTP com arquivo
            response = HttpResponse(
                excel_file.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            return response

        except Http404:
            # Re-raise Http404 para retornar 404 corretamente
            raise
        except Exception as e:
            return Response(
                {"error": f"Erro ao gerar Excel: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """
        Retorna estatísticas gerais de payrolls (independente de filtros de paginação).

        GET /payrolls/stats/

        Returns:
            {
                "total": <count>,
                "draft": <count>,
                "paid": <count>
            }
        """
        from django.db.models import Count

        queryset = self.get_queryset()  # Já filtra por empresa do usuário

        total_count = queryset.count()
        draft_count = queryset.filter(status="DRAFT").count()
        paid_count = queryset.filter(status="PAID").count()

        return Response(
            {
                "total": total_count,
                "draft": draft_count,
                "paid": paid_count,
            }
        )


# ==============================================================================
# DASHBOARD VIEW PROTEGIDA
# ==============================================================================

from rest_framework.views import APIView
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta


class ProtectedDashboardView(APIView):
    """
    Dashboard protegido - apenas Customer Admin pode acessar.
    Mostra estatísticas da empresa do usuário logado com agregações otimizadas.

    Query Parameters:
        - period: '7d', '30d', '90d', '1y', 'all' (default: '30d')
        - start_date: YYYY-MM-DD (custom period start)
        - end_date: YYYY-MM-DD (custom period end)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna estatísticas filtradas por empresa com agregações otimizadas"""
        user = request.user

        # Apenas Customer Admin tem acesso ao dashboard
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

        # Calculate date range based on period
        if start_date and end_date:
            # Custom date range
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Predefined period
            end = datetime.now().date()
            if period == "7d":
                start = end - timedelta(days=7)
            elif period == "30d":
                start = end - timedelta(days=30)
            elif period == "90d":
                start = end - timedelta(days=90)
            elif period == "1y":
                start = end - timedelta(days=365)
            else:  # 'all'
                start = None

        # Base queryset: Payrolls da empresa do usuário
        company_payrolls = Payroll.objects.filter(provider__company=user.company)

        # Apply date filter using reference_month (MM/YYYY format)
        # For period filters, convert to month comparison
        if start and period != "all":
            # Convert start date to MM/YYYY format
            start_ref = start.strftime("%m/%Y")
            end_ref = end.strftime("%m/%Y")

            # Filter by reference_month range
            # Note: This filters months lexicographically, which works for MM/YYYY
            # Get all months in the date range
            from datetime import date as dt_date
            from dateutil.relativedelta import relativedelta

            months_in_range = []
            current = start.replace(day=1)
            end_month = end.replace(day=1)

            while current <= end_month:
                months_in_range.append(current.strftime("%m/%Y"))
                current = current + relativedelta(months=1)

            company_payrolls = company_payrolls.filter(
                reference_month__in=months_in_range
            )

        # Aggregate stats by status
        from decimal import Decimal

        draft_stats = company_payrolls.filter(status="DRAFT").aggregate(
            count=Count("id"), total=Sum("net_value")
        )
        closed_stats = company_payrolls.filter(status="CLOSED").aggregate(
            count=Count("id"), total=Sum("net_value")
        )
        paid_stats = company_payrolls.filter(status="PAID").aggregate(
            count=Count("id"), total=Sum("net_value")
        )

        total_payrolls = company_payrolls.count()
        total_value = company_payrolls.aggregate(Sum("net_value"))[
            "net_value__sum"
        ] or Decimal("0")

        # Estatísticas principais
        stats = {
            "total_providers": Provider.objects.filter(company=user.company).count(),
            "payrolls": {
                "total": total_payrolls,
                "draft": draft_stats["count"] or 0,
                "closed": closed_stats["count"] or 0,
                "paid": paid_stats["count"] or 0,
            },
            "financial": {
                "total_value": float(total_value),
                "pending_value": float(closed_stats["total"] or Decimal("0")),
                "paid_value": float(paid_stats["total"] or Decimal("0")),
                "average_payroll": (
                    float(total_value / total_payrolls) if total_payrolls > 0 else 0
                ),
            },
        }

        # Monthly aggregation using optimized Django ORM
        monthly_aggregated = (
            company_payrolls.values("reference_month", "status")
            .annotate(count=Count("id"), total_value=Sum("net_value"))
            .order_by("reference_month", "status")
        )

        # Transform result into desired structure
        monthly_data = {}
        for item in monthly_aggregated:
            month = item["reference_month"]
            status = item["status"].lower()

            if month not in monthly_data:
                monthly_data[month] = {
                    "draft": {"count": 0, "value": 0},
                    "closed": {"count": 0, "value": 0},
                    "paid": {"count": 0, "value": 0},
                    "total_count": 0,
                    "total_value": 0,
                    "avg_value": 0,
                }

            monthly_data[month][status] = {
                "count": item["count"],
                "value": float(item["total_value"] or Decimal("0")),
            }

            # Update totals
            monthly_data[month]["total_count"] += item["count"]
            monthly_data[month]["total_value"] += float(
                item["total_value"] or Decimal("0")
            )

        # Calculate averages
        for month in monthly_data:
            count = monthly_data[month]["total_count"]
            if count > 0:
                monthly_data[month]["avg_value"] = (
                    monthly_data[month]["total_value"] / count
                )

        # Calculate trends
        trends = {
            "monthly_growth_percentage": 0,
        }

        # Calculate monthly growth (last month vs previous month)
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
            if prev_total > 0:
                trends["monthly_growth_percentage"] = (
                    (last_total - prev_total) / prev_total
                ) * 100

        # Recent activity (últimos 10 payrolls)
        recent_payrolls = company_payrolls.select_related("provider").order_by(
            "-created_at"
        )[:10]
        from .serializers import PayrollSerializer

        recent_activity = PayrollSerializer(recent_payrolls, many=True).data

        return Response(
            {
                "stats": stats,
                "monthly_aggregation": monthly_data,
                "trends": trends,
                "recent_activity": recent_activity,
            }
        )
