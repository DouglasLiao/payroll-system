from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


# ==============================================================================
# PERMISSION CLASSES
# ==============================================================================


class IsSuperAdmin(permissions.BasePermission):
    """Permissão para Super Admin apenas"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "SUPER_ADMIN"


class IsCustomerAdmin(permissions.BasePermission):
    """Permissão para Customer Admin apenas"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CUSTOMER_ADMIN"


class IsProvider(permissions.BasePermission):
    """Permissão para Provider apenas"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "PROVIDER"


class IsCustomerAdminOrReadOnly(permissions.BasePermission):
    """Permite leitura para todos autenticados, escrita apenas para Customer Admin"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == "CUSTOMER_ADMIN"


# ==============================================================================
# DECORATORS PARA VALIDAÇÃO DE ROLE
# ==============================================================================


def require_role(*allowed_roles):
    """
    Decorator para validar role do usuário em function-based views.

    Uso:
        @api_view(['GET'])
        @require_role('SUPER_ADMIN')
        def my_view(request):
            ...

        @api_view(['POST'])
        @require_role('CUSTOMER_ADMIN', 'SUPER_ADMIN')
        def another_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Autenticação necessária"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if request.user.role not in allowed_roles:
                return Response(
                    {
                        "error": f'Acesso negado. Roles permitidas: {", ".join(allowed_roles)}'
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def super_admin_only(view_func):
    """Decorator para endpoints exclusivos de Super Admin"""
    return require_role("SUPER_ADMIN")(view_func)


def customer_admin_only(view_func):
    """Decorator para endpoints exclusivos de Customer Admin"""
    return require_role("CUSTOMER_ADMIN")(view_func)


def provider_only(view_func):
    """Decorator para endpoints exclusivos de Provider"""
    return require_role("PROVIDER")(view_func)


def admin_only(view_func):
    """Decorator para endpoints de Super Admin ou Customer Admin"""
    return require_role("SUPER_ADMIN", "CUSTOMER_ADMIN")(view_func)
