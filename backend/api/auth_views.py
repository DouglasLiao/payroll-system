from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from .serializers import UserSerializer
from .permissions import require_role, super_admin_only, customer_admin_only


# ==============================================================================
# AUTHENTICATION VIEWS
# ==============================================================================


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login endpoint com cookies para persistência de sessão"""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Permitir login com email ou username
        # Se 'email' foi enviado, tentar encontrar o username correspondente
        if "email" in request.data and "username" not in request.data:
            from .models import User

            try:
                user = User.objects.get(email=request.data["email"])
                request.data._mutable = True
                request.data["username"] = user.username
                request.data._mutable = False
            except User.DoesNotExist:
                return Response(
                    {"detail": "Email ou senha inválidos"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Armazenar tokens em httpOnly cookies
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            # Cookie para access token (expira em 1 hora)
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
                max_age=3600,  # 1 hora
            )

            # Cookie para refresh token (expira em 7 dias)
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
                max_age=604800,  # 7 dias
            )

            # Adicionar informações do usuário
            from .models import User

            try:
                user = User.objects.get(username=request.data.get("username"))
                response.data["user"] = UserSerializer(user).data
            except User.DoesNotExist:
                pass

        return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Retorna informações do usuário logado incluindo timeout configurado"""
    serializer = UserSerializer(request.user)
    data = serializer.data

    # Adicionar timeout de inatividade (padrão ou personalizado do usuário)
    data["inactivity_timeout"] = getattr(
        request.user, "inactivity_timeout", settings.SESSION_INACTIVITY_TIMEOUT
    )

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Altera senha do usuário"""
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response(
            {"error": "old_password e new_password são obrigatórios"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.check_password(old_password):
        return Response(
            {"error": "Senha atual incorreta"}, status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()
    return Response({"message": "Senha alterada com sucesso"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_timeout_preference(request):
    """Atualiza preferência de timeout de inatividade do usuário"""
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

    # Validar timeout (mínimo 60s, máximo 3600s = 1 hora)
    if timeout < 60 or timeout > 3600:
        return Response(
            {"error": "Timeout deve estar entre 60 e 3600 segundos"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    request.user.inactivity_timeout = timeout
    request.user.save()

    return Response({"message": "Timeout atualizado com sucesso", "timeout": timeout})


@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    """Logout do usuário removendo cookies"""
    response = Response({"message": "Logout realizado com sucesso"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
