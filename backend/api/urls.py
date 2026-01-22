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

router = DefaultRouter()
router.register(r"providers", ProviderViewSet)
router.register(r"payrolls", PayrollViewSet)
router.register(r"companies", CompanyViewSet)

urlpatterns = [
    # Authentication endpoints
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", current_user, name="current_user"),
    path("auth/change-password/", change_password, name="change_password"),
    path("auth/update-timeout/", update_timeout_preference, name="update_timeout"),
    path("auth/logout/", logout, name="logout"),
    # Existing routes
    path("", include(router.urls)),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("receipt/<int:pk>/", generate_receipt, name="download-receipt"),
]
