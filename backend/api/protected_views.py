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


# ==============================================================================
# DASHBOARD VIEW PROTEGIDA
# ==============================================================================

from rest_framework.views import APIView
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta


class ProtectedDashboardView(APIView):
    """
    Dashboard protegido - apenas Customer Admin pode acessar.
    Mostra estatísticas da empresa do usuário logado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna estatísticas filtradas por empresa"""
        user = request.user

        # Apenas Customer Admin tem acesso ao dashboard
        if user.role != "CUSTOMER_ADMIN":
            return Response(
                {
                    "error": "Acesso negado. Apenas Customer Admin pode acessar o dashboard."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Filtrar payrolls pela empresa do usuário
        company_payrolls = Payroll.objects.filter(provider__company=user.company)

        # Estatísticas
        stats = {
            "total_providers": Provider.objects.filter(company=user.company).count(),
            "total_payrolls": company_payrolls.count(),
            "draft_payrolls": company_payrolls.filter(status="DRAFT").count(),
            "closed_payrolls": company_payrolls.filter(status="CLOSED").count(),
            "paid_payrolls": company_payrolls.filter(status="PAID").count(),
            "total_pending": company_payrolls.filter(status="CLOSED").aggregate(
                Sum("net_value")
            )["net_value__sum"]
            or 0,
            "total_paid": company_payrolls.filter(status="PAID").aggregate(
                Sum("net_value")
            )["net_value__sum"]
            or 0,
        }

        # Atividades recentes (últimos 10 payrolls)
        recent_payrolls = company_payrolls.order_by("-created_at")[:10]
        from .serializers import PayrollSerializer

        recent_activity = PayrollSerializer(recent_payrolls, many=True).data

        return Response(
            {
                "stats": stats,
                "recent_activity": recent_activity,
            }
        )
