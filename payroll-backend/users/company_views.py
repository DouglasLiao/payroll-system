import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services.company_service import (
    CompanyService,
    CompanyAlreadyActiveError,
)
from services.user_service import (
    UserService,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
)
from site_manage.selectors import (
    company_list_filtered,
    user_list_for_company,
    provider_list_for_user,
)
from users.models import UserRole
from site_manage.serializers import ProviderSerializer

from .permissions import IsSuperAdmin
from .serializers import (
    CompanySerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Gerenciamento de empresas — apenas Super Admin.
    Reads via selectors, writes via CompanyService/UserService.
    """

    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_queryset(self):
        params = self.request.query_params
        is_active_raw = params.get("is_active")
        is_active = None
        if is_active_raw is not None:
            is_active = is_active_raw.lower() in ["true", "1"]
        return company_list_filtered(
            is_active=is_active,
            search=params.get("search"),
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == 1:
            return Response(
                {"error": "A empresa Super Admin não pode ser excluída."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """POST /users/companies/{id}/approve/"""
        company = self.get_object()
        try:
            company = CompanyService.approve_company(company=company)
        except CompanyAlreadyActiveError as e:
            return Response({"message": str(e)}, status=status.HTTP_200_OK)

        CompanyService.notify_approval(company=company)
        return Response(
            {"message": f"Empresa {company.name} aprovada com sucesso!"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        """POST /users/companies/{id}/toggle-status/"""
        company = self.get_object()
        company = CompanyService.toggle_company_status(company=company)
        status_msg = "ativada" if company.is_active else "desativada"
        return Response(
            {
                "message": f"Empresa {company.name} {status_msg} com sucesso!",
                "is_active": company.is_active,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """POST /users/companies/{id}/reject/"""
        company = self.get_object()
        CompanyService.notify_rejection(company=company)
        company_name = CompanyService.reject_company(company=company)
        return Response(
            {"message": f"Empresa {company_name} rejeitada e removida com sucesso!"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="create-admin")
    def create_admin(self, request, pk=None):
        """POST /users/companies/{id}/create-admin/"""
        company = self.get_object()
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not all([username, email, password]):
            return Response(
                {"error": "username, email e password são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = UserService.create_customer_admin(
                username=username,
                email=email,
                password=password,
                company=company,
                first_name=request.data.get("first_name", ""),
                last_name=request.data.get("last_name", ""),
            )
        except (EmailAlreadyExistsError, UsernameAlreadyExistsError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def admins(self, request, pk=None):
        """GET /users/companies/{id}/admins/"""
        company = self.get_object()
        admins = user_list_for_company(company=company, role=UserRole.CUSTOMER_ADMIN)
        return Response(UserSerializer(admins, many=True).data)

    @action(detail=True, methods=["get"])
    def providers(self, request, pk=None):
        """GET /users/companies/{id}/providers/"""
        company = self.get_object()
        providers = provider_list_for_user(user=request.user).filter(company=company)
        return Response(ProviderSerializer(providers, many=True).data)
