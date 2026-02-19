"""
users/urls.py — URL routes for the users/ app.

All routes are mounted under /users/ in core/urls.py.

Auth:         /users/auth/...
Companies:    /users/companies/
Subscriptions:/users/subscriptions/
Math Templates:/users/math-templates/
Payroll Configs:/users/payroll-configs/
Super Admin:  /users/super-admin/stats/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    # Auth
    CustomTokenObtainPairView,
    current_user,
    change_password,
    update_timeout_preference,
    logout,
    # Registration & Password Reset
    check_email,
    register,
    password_reset_request,
    password_reset_confirm,
    # ViewSets,
    PayrollMathTemplateViewSet,
    PayrollConfigurationViewSet,
    SubscriptionViewSet,
    SuperAdminStatsViewSet,
    CompanyViewSet,
)


router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")
router.register(r"math-templates", PayrollMathTemplateViewSet, basename="math-template")
router.register(
    r"payroll-configs", PayrollConfigurationViewSet, basename="payroll-config"
)
router.register(
    r"super-admin/stats", SuperAdminStatsViewSet, basename="super-admin-stats"
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path(
        "auth/token/",
        CustomTokenObtainPairView.as_view(),
        name="users_token_obtain_pair",
    ),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="users_token_refresh"),
    path("auth/me/", current_user, name="users_current_user"),
    path("auth/logout/", logout, name="users_logout"),
    path("auth/change-password/", change_password, name="users_change_password"),
    path(
        "auth/update-timeout/", update_timeout_preference, name="users_update_timeout"
    ),
    # ── Registration ──────────────────────────────────────────────────────────
    path("auth/check-email/", check_email, name="users_check_email"),
    path("auth/register/", register, name="users_register"),
    path(
        "auth/password-reset/request/",
        password_reset_request,
        name="users_password_reset_request",
    ),
    path(
        "auth/password-reset/confirm/",
        password_reset_confirm,
        name="users_password_reset_confirm",
    ),
    # ── ViewSets ──────────────────────────────────────────────────────────────
    path("", include(router.urls)),
]
