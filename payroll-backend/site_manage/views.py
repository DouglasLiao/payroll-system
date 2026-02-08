from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers
from django.utils import timezone
from datetime import timedelta
import secrets
import logging

from .models import (
    Payment,
    User,
    PasswordResetToken,
    Company,
    PayrollConfiguration,
    Subscription,
    UserRole,
)
from utils.redis_publisher import event_publisher

logger = logging.getLogger(__name__)


def generate_receipt(request, pk):
    """
    Simple Text Receipt for MVP.

    Kept for legacy compatibility - generates a simple text receipt for payments.
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


# ==============================================================================
# PASSWORD RESET VIEWS
# ==============================================================================


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

    def validate_token(self, value):
        try:
            token_obj = PasswordResetToken.objects.get(token=value)
            if not token_obj.is_valid():
                raise serializers.ValidationError("Token inválido ou expirado.")
            self.context["token_obj"] = token_obj
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")
        return value


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request password reset - POST /auth/password-reset/request/"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]

    try:
        user = User.objects.get(email=email)
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)

        PasswordResetToken.objects.create(user=user, token=token, expires_at=expires_at)

        event_publisher.publish_password_reset_requested(
            user_email=user.email,
            token=token,
            user_name=user.get_full_name() or user.username,
            tenant_id=str(user.company_id) if user.company_id else None,
        )

        logger.info(f"Password reset requested for user: {user.username}")

    except User.DoesNotExist:
        logger.warning(f"Password reset requested for non-existent email: {email}")
        pass

    return Response(
        {
            "message": "Se o email estiver cadastrado, você receberá instruções para redefinir sua senha."
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset - POST /auth/password-reset/confirm/"""
    serializer = PasswordResetConfirmSerializer(data=request.data, context={})
    serializer.is_valid(raise_exception=True)

    token_obj = serializer.context["token_obj"]
    new_password = serializer.validated_data["new_password"]

    user = token_obj.user
    user.set_password(new_password)
    user.save()

    token_obj.used = True
    token_obj.used_at = timezone.now()
    token_obj.save()

    logger.info(f"Password reset completed for user: {user.username}")

    return Response(
        {
            "message": "Senha redefinida com sucesso! Você já pode fazer login com sua nova senha."
        },
        status=status.HTTP_200_OK,
    )


# ============================================================================
# Registration Endpoints
# ============================================================================

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


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
    first_name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    last_name = serializers.CharField(required=False, max_length=150, allow_blank=True)

    # Company Fields
    company_name = serializers.CharField(required=True, max_length=255)
    company_cnpj = serializers.CharField(required=True, max_length=18)
    company_phone = serializers.CharField(
        required=False, max_length=20, allow_blank=True
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está cadastrado.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem."}
            )

        # Django password validation
        try:
            validate_password(data["password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data


@api_view(["POST"])
@permission_classes([AllowAny])
def check_email(request):
    """Check if email is already registered - POST /auth/check-email/"""
    serializer = CheckEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    exists = User.objects.filter(email=email).exists()

    return Response(
        {"email": email, "exists": exists, "available": not exists},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Register a new user - POST /auth/register/"""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        # 1. Create Company (Inactive by default)
        company = Company.objects.create(
            name=serializer.validated_data["company_name"],
            cnpj=serializer.validated_data["company_cnpj"],
            phone=serializer.validated_data.get("company_phone", ""),
            is_active=False,  # Requires approval
        )

        # 2. Create Default Configuration
        PayrollConfiguration.objects.create(company=company)

        # 3. Create Default Subscription (Basic)
        Subscription.objects.create(
            company=company,
            start_date=timezone.now().date(),
            is_active=True,  # Subscription exists, but company is inactive
        )

        # 4. Create User as CUSTOMER_ADMIN linked to Company
        user = User.objects.create_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
            role=UserRole.CUSTOMER_ADMIN,
            company=company,
        )

        logger.info(f"New user registered: {user.username} ({user.email})")

        # TODO: Send welcome email (optional)
        # from utils.redis_publisher import event_publisher
        # event_publisher.publish_welcome_email(user.email, user.get_full_name() or user.username)

        return Response(
            {
                "message": "Conta criada com sucesso! Você já pode fazer login.",
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

    except Exception as e:
        logger.error(f"Error during registration: {e}", exc_info=True)
        return Response(
            {"message": "Erro ao criar conta. Tente novamente."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
