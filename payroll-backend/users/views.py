"""
users/views.py — All user, auth, company, and subscription views.

Views are THIN ORCHESTRATORS: validate input → call service/selector → serialize response.
Zero direct model access. All business logic lives in services/.
All read queries live in site_manage/selectors.py.

Sections:
  1. AUTH          — Login, logout, current user, password change, timeout
  2. REGISTRATION  — Register, check email, password reset
  3. COMPANIES     — CompanyViewSet (Super Admin)
  4. CONFIG        — PayrollMathTemplateViewSet, PayrollConfigurationViewSet
  5. SUBSCRIPTIONS — SubscriptionViewSet
  6. STATS         — SuperAdminStatsViewSet
"""

import logging

from django.conf import settings

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

# ── Services ──────────────────────────────────────────────────────────────────
from users.services.user_service import (
    InvalidPasswordError,
    InvalidTokenError,
    PayrollConfigService,
    SubscriptionService,
    UserService,
    UserServiceError,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
)


from site_manage.selectors import (
    company_get_by_id,
    math_template_get_by_id,
    super_admin_stats,
    company_list_filtered,
    user_list_for_company,
    provider_list_for_user,
)

# ── Utilities ─────────────────────────────────────────────────────────────────
from utils.redis_publisher import event_publisher

from .permissions import IsSuperAdmin
from .serializers import (
    CompanySerializer,
    SubscriptionSerializer,
    UserSerializer,
)

# ── Selectors (read-only queries) ─────────────────────────────────────────────

from site_manage.services.company_service import (
    CompanyService,
    CompanyAlreadyActiveError,
)

from users.models import UserRole
from site_manage.serializers import ProviderSerializer


logger = logging.getLogger(__name__)


# ==============================================================================
# 1. AUTH
# ==============================================================================


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login endpoint — aceita email ou username, armazena tokens em cookies httpOnly."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        raw_identifier = data.get("username") or data.get("email", "")

        # Resolve email → username before passing to JWT (which requires username)
        resolved_user = UserService.get_user_by_email_or_username(
            identifier=raw_identifier
        )
        if resolved_user and raw_identifier != resolved_user.username:
            if hasattr(data, "_mutable"):
                data._mutable = True
            data["username"] = resolved_user.username
            if hasattr(data, "_mutable"):
                data._mutable = False

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")
            cookie_kwargs = {
                "httponly": True,
                "secure": settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                "samesite": settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            }
            response.set_cookie(
                "access_token", access_token, max_age=3600, **cookie_kwargs
            )
            response.set_cookie(
                "refresh_token", refresh_token, max_age=604800, **cookie_kwargs
            )

            user = resolved_user or UserService.get_user_by_email_or_username(
                identifier=request.data.get("username", "")
            )
            if user:
                response.data["user"] = UserSerializer(user).data

        return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Retorna informações do usuário logado incluindo timeout configurado."""
    data = UserSerializer(request.user).data
    data["inactivity_timeout"] = getattr(
        request.user, "inactivity_timeout", settings.SESSION_INACTIVITY_TIMEOUT
    )
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Altera senha do usuário via UserService."""
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response(
            {"error": "old_password e new_password são obrigatórios"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        UserService.change_password(
            user=request.user,
            old_password=old_password,
            new_password=new_password,
        )
    except InvalidPasswordError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Senha alterada com sucesso"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_timeout_preference(request):
    """Atualiza preferência de timeout de inatividade via UserService."""
    timeout = request.data.get("timeout")
    if timeout is None:
        return Response(
            {"error": "timeout é obrigatório"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        timeout = int(timeout)
    except (ValueError, TypeError):
        return Response(
            {"error": "timeout deve ser um número inteiro"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = UserService.update_timeout_preference(
            user=request.user, timeout_seconds=timeout
        )
    except UserServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "message": "Timeout atualizado com sucesso",
            "timeout": user.inactivity_timeout,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    """Logout do usuário removendo cookies."""
    response = Response({"message": "Logout realizado com sucesso"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


# ==============================================================================
# 2. REGISTRATION & PASSWORD RESET
# ==============================================================================


class CheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, min_length=3, max_length=150)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    password_confirm = serializers.CharField(
        required=True, min_length=8, write_only=True
    )
    first_name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    last_name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    company_name = serializers.CharField(required=True, max_length=255)
    company_cnpj = serializers.CharField(required=True, max_length=18)
    company_phone = serializers.CharField(
        required=False, max_length=20, allow_blank=True
    )

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem."}
            )
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=255)
    new_password = serializers.CharField(
        required=True, min_length=8, max_length=128, write_only=True
    )
    new_password_confirm = serializers.CharField(
        required=True, min_length=8, max_length=128, write_only=True
    )

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "As senhas não coincidem."}
            )
        return data


@api_view(["POST"])
@permission_classes([AllowAny])
def check_email(request):
    """POST /users/auth/check-email/"""
    serializer = CheckEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    available = UserService.email_is_available(email=email)
    return Response({"email": email, "exists": not available, "available": available})


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """POST /users/auth/register/ — delegates to CompanyService.register_company()"""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data

    try:
        company, user = CompanyService.register_company(
            company_name=d["company_name"],
            company_cnpj=d["company_cnpj"],
            company_phone=d.get("company_phone", ""),
            admin_username=d["username"],
            admin_email=d["email"],
            admin_password=d["password"],
            admin_first_name=d.get("first_name", ""),
            admin_last_name=d.get("last_name", ""),
        )
    except (EmailAlreadyExistsError, UsernameAlreadyExistsError) as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error during registration: {e}", exc_info=True)
        return Response(
            {"message": "Erro ao criar conta. Tente novamente."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    CompanyService.notify_registration(company=company, user=user)

    return Response(
        {
            "message": "Conta criada com sucesso! Aguardando aprovação.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "company": {
                    "id": company.id,
                    "name": company.name,
                    "status": "PENDING_APPROVAL",
                },
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    """POST /users/auth/password-reset/request/ — delegates to UserService"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token_obj = UserService.request_password_reset(
        email=serializer.validated_data["email"]
    )

    if token_obj:
        try:
            event_publisher.publish_password_reset_requested(
                user_email=token_obj.user.email,
                token=token_obj.token,
                user_name=token_obj.user.get_full_name() or token_obj.user.username,
                tenant_id=(
                    str(token_obj.user.company_id)
                    if token_obj.user.company_id
                    else None
                ),
            )
        except Exception as e:
            logger.error(f"Failed to publish password reset event: {e}")

    # Always 200 — don't reveal if email exists
    return Response(
        {
            "message": "Se o email estiver cadastrado, você receberá instruções para redefinir sua senha."
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """POST /users/auth/password-reset/confirm/ — delegates to UserService"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        UserService.confirm_password_reset(
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )
    except InvalidTokenError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except InvalidPasswordError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "message": "Senha redefinida com sucesso! Você já pode fazer login com sua nova senha."
        },
        status=status.HTTP_200_OK,
    )


# ==============================================================================
# 4. PAYROLL CONFIG & MATH TEMPLATES
# ==============================================================================

# ==============================================================================
# 3. COMPANIES
# ==============================================================================


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


class PayrollMathTemplateViewSet(viewsets.ModelViewSet):
    """CRUD completo para Templates de Cálculo — apenas Super Admin."""

    permission_classes = [IsSuperAdmin]

    def get_serializer_class(self):
        from site_manage.serializers import PayrollMathTemplateSerializer

        return PayrollMathTemplateSerializer

    def get_queryset(self):
        from site_manage.selectors import math_template_list

        return math_template_list()


class PayrollConfigurationViewSet(viewsets.ModelViewSet):
    """Gerenciamento de configurações de folha das empresas."""

    permission_classes = [IsSuperAdmin]

    def get_serializer_class(self):
        from site_manage.serializers import PayrollConfigurationSerializer

        return PayrollConfigurationSerializer

    def get_queryset(self):
        from site_manage.selectors import payroll_config_list

        return payroll_config_list(
            company_id=self.request.query_params.get("company_id")
        )

    @action(detail=False, methods=["post"], url_path="apply-template")
    def apply_template(self, request):
        """Body: { "company_id": 1, "template_id": 1 }"""
        company_id = request.data.get("company_id")
        template_id = request.data.get("template_id")

        if not company_id or not template_id:
            return Response(
                {"error": "company_id e template_id são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = company_get_by_id(company_id=company_id)
        template = math_template_get_by_id(template_id=template_id)

        if not company:
            return Response(
                {"error": "Empresa não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )
        if not template:
            return Response(
                {"error": "Template não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        config = PayrollConfigService.apply_template(company=company, template=template)
        return Response(self.get_serializer(config).data, status=status.HTTP_200_OK)


# ==============================================================================
# 5. SUBSCRIPTIONS
# ==============================================================================


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Gerenciamento de Assinaturas — apenas Super Admin."""

    serializer_class = SubscriptionSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        from site_manage.selectors import subscription_list

        return subscription_list(company_id=self.request.query_params.get("company_id"))

    @action(detail=True, methods=["post"], url_path="renew")
    def renew(self, request, pk=None):
        """Body: { "plan_type": "PRO", "end_date": "2030-12-31" (opcional) }"""
        subscription = self.get_object()
        try:
            subscription = SubscriptionService.renew_subscription(
                subscription=subscription,
                plan_type=request.data.get("plan_type"),
                end_date=request.data.get("end_date"),
            )
        except UserServiceError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(subscription).data)


# ==============================================================================
# 6. SUPER ADMIN STATS
# ==============================================================================


class SuperAdminStatsViewSet(viewsets.ViewSet):
    """Estatísticas globais para o Dashboard do Super Admin."""

    permission_classes = [IsSuperAdmin]

    def list(self, request):
        return Response(super_admin_stats())
