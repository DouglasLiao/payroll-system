from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import generate_receipt

# Import protected ViewSets for multi-tenancy
from .protected_views import (
    ProtectedProviderViewSet as ProviderViewSet,
    ProtectedPayrollViewSet as PayrollViewSet,
    ProtectedDashboardView as DashboardView,
)
from .auth_views import (
    CustomTokenObtainPairView,
    current_user,
    change_password,
    update_timeout_preference,
    logout,
)
from .company_views import CompanyViewSet
from .views import password_reset_request, password_reset_confirm, check_email, register
from .payroll_config_views import (
    PayrollMathTemplateViewSet,
    PayrollConfigurationViewSet,
    SubscriptionViewSet,
    SuperAdminStatsViewSet,
)

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")

# Rotas protegidas para Payrolls
router.register(r"payrolls", PayrollViewSet, basename="payroll")
router.register(r"providers", ProviderViewSet, basename="provider")
# Super Admin Configurations
router.register(r"math-templates", PayrollMathTemplateViewSet, basename="math-template")
router.register(
    r"payroll-configs", PayrollConfigurationViewSet, basename="payroll-config"
)
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")
router.register(
    r"super-admin/stats", SuperAdminStatsViewSet, basename="super-admin-stats"
)

urlpatterns = [
    # Auth endpoints
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/me/", current_user, name="current_user"),
    path("auth/change-password/", change_password, name="change_password"),
    path("auth/update-timeout/", update_timeout_preference, name="update_timeout"),
    path("auth/logout/", logout, name="logout"),
    # Registration endpoints
    path("auth/check-email/", check_email, name="check_email"),
    path("auth/register/", register, name="register"),
    # Password reset endpoints
    path(
        "auth/password-reset/request/",
        password_reset_request,
        name="password_reset_request",
    ),
    path(
        "auth/password-reset/confirm/",
        password_reset_confirm,
        name="password_reset_confirm",
    ),
    # Existing routes
    path("", include(router.urls)),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("receipt/<int:pk>/", generate_receipt, name="download-receipt"),
]
