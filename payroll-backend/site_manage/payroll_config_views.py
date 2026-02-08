from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from django.utils import timezone
from decimal import Decimal

from .models import (
    PayrollMathTemplate,
    PayrollConfiguration,
    Subscription,
    Company,
    Provider,
    Payroll,
    PlanType,
)
from .serializers import (
    PayrollMathTemplateSerializer,
    PayrollConfigurationSerializer,
    SubscriptionSerializer,
)
from .permissions import IsSuperAdmin


class PayrollMathTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para Templates de Cálculo.
    Acesso restrito a Super Admin.
    """

    queryset = PayrollMathTemplate.objects.all().order_by("name")
    serializer_class = PayrollMathTemplateSerializer
    permission_classes = [IsSuperAdmin]


class PayrollConfigurationViewSet(viewsets.ModelViewSet):
    """
    Gerenciamento de configurações de folha das empresas.
    Permite buscar por company_id ou ID da config.
    """

    queryset = PayrollConfiguration.objects.all()
    serializer_class = PayrollConfigurationSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        """
        Permite filtrar por empresa: /api/payroll-configs/?company_id=1
        """
        queryset = super().get_queryset()
        company_id = self.request.query_params.get("company_id")
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        return queryset

    @action(detail=False, methods=["post"], url_path="apply-template")
    def apply_template(self, request):
        """
        Aplica um MathTemplate a uma Empresa.
        Body: { "company_id": 1, "template_id": 1 }
        """
        company_id = request.data.get("company_id")
        template_id = request.data.get("template_id")

        if not company_id or not template_id:
            return Response(
                {"error": "company_id e template_id são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = get_object_or_404(Company, pk=company_id)
        template = get_object_or_404(PayrollMathTemplate, pk=template_id)

        # Get or create config
        config, created = PayrollConfiguration.objects.get_or_create(company=company)

        # Copy values
        config.overtime_percentage = template.overtime_percentage
        config.night_shift_percentage = template.night_shift_percentage
        config.holiday_percentage = template.holiday_percentage
        config.advance_percentage = template.advance_percentage
        config.transport_voucher_type = template.transport_voucher_type
        config.business_days_rule = template.business_days_rule
        config.save()

        serializer = self.get_serializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Gerenciamento de Assinaturas.
    """

    queryset = Subscription.objects.all().order_by("-created_at")
    serializer_class = SubscriptionSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        """
        Permite filtrar por empresa: /api/subscriptions/?company_id=1
        """
        queryset = super().get_queryset()
        company_id = self.request.query_params.get("company_id")
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        return queryset

    @action(detail=True, methods=["post"], url_path="renew")
    def renew(self, request, pk=None):
        """
        Renova a assinatura ou altera o plano.
        Body: { "plan_type": "PRO", "end_date": "2030-12-31" (opcional) }
        """
        subscription = self.get_object()
        plan_type = request.data.get("plan_type")
        end_date = request.data.get("end_date")

        if plan_type:
            if plan_type not in PlanType.values:
                return Response(
                    {"error": "Plano inválido"}, status=status.HTTP_400_BAD_REQUEST
                )
            subscription.plan_type = plan_type
            # Reset values to default for the new plan (will be handled by save() method if None)
            subscription.max_providers = None
            subscription.price = None

        if end_date:
            subscription.end_date = end_date

        subscription.save()
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)


class SuperAdminStatsViewSet(viewsets.ViewSet):
    """
    Estatísticas globais para o Dashboard do Super Admin.
    """

    permission_classes = [IsSuperAdmin]

    def list(self, request):
        total_companies = Company.objects.count()
        total_providers = Provider.objects.count()
        active_subscriptions = Subscription.objects.filter(
            is_active=True, end_date__gte=timezone.now().date()
        ).count()

        # Simple MRR calculation (Sum of price of active subscriptions)
        mrr = Subscription.objects.filter(
            is_active=True, end_date__gte=timezone.now().date()
        ).aggregate(Sum("price"))["price__sum"] or Decimal("0.00")

        # Companies pending approval (Placeholder logic - assuming all are active for now, or check is_active=False)
        pending_approvals = Company.objects.filter(is_active=False).count()

        return Response(
            {
                "total_companies": total_companies,
                "total_providers": total_providers,
                "active_subscriptions": active_subscriptions,
                "mrr": mrr,
                "pending_approvals": pending_approvals,
            }
        )
