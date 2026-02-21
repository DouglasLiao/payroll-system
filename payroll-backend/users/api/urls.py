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

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CompanyAdminsAPIView,
    CompanyApproveAPIView,
    CompanyCreateAdminAPIView,
    CompanyDetailAPIView,
    # Companies
    CompanyListAPIView,
    CompanyProvidersAPIView,
    CompanyRejectAPIView,
    CompanyToggleStatusAPIView,
    # Auth
    CustomTokenObtainPairView,
    PayrollConfigurationApplyTemplateAPIView,
    PayrollConfigurationDetailAPIView,
    PayrollConfigurationListCreateAPIView,
    PayrollMathTemplateDetailAPIView,
    # Config
    PayrollMathTemplateListCreateAPIView,
    SubscriptionDetailAPIView,
    # Subscriptions
    SubscriptionListAPIView,
    SubscriptionRenewAPIView,
    # Stats
    SuperAdminStatsAPIView,
    change_password,
    # Registration & Password Reset
    check_email,
    current_user,
    logout,
    password_reset_confirm,
    password_reset_request,
    register,
    update_timeout_preference,
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
    # ── Companies ────────────────────────────────────────────────────────────
    path("companies/", CompanyListAPIView.as_view(), name="company-list"),
    path("companies/<int:pk>/", CompanyDetailAPIView.as_view(), name="company-detail"),
    path(
        "companies/<int:pk>/approve/",
        CompanyApproveAPIView.as_view(),
        name="company-approve",
    ),
    path(
        "companies/<int:pk>/toggle-status/",
        CompanyToggleStatusAPIView.as_view(),
        name="company-toggle-status",
    ),
    path(
        "companies/<int:pk>/reject/",
        CompanyRejectAPIView.as_view(),
        name="company-reject",
    ),
    path(
        "companies/<int:pk>/create-admin/",
        CompanyCreateAdminAPIView.as_view(),
        name="company-create-admin",
    ),
    path(
        "companies/<int:pk>/admins/",
        CompanyAdminsAPIView.as_view(),
        name="company-admins",
    ),
    path(
        "companies/<int:pk>/providers/",
        CompanyProvidersAPIView.as_view(),
        name="company-providers",
    ),
    # ── Subscriptions ────────────────────────────────────────────────────────
    path("subscriptions/", SubscriptionListAPIView.as_view(), name="subscription-list"),
    path(
        "subscriptions/<int:pk>/",
        SubscriptionDetailAPIView.as_view(),
        name="subscription-detail",
    ),
    path(
        "subscriptions/<int:pk>/renew/",
        SubscriptionRenewAPIView.as_view(),
        name="subscription-renew",
    ),
    # ── Payroll Math Templates ───────────────────────────────────────────────
    path(
        "math-templates/",
        PayrollMathTemplateListCreateAPIView.as_view(),
        name="math-template-list-create",
    ),
    path(
        "math-templates/<int:pk>/",
        PayrollMathTemplateDetailAPIView.as_view(),
        name="math-template-detail",
    ),
    # ── Payroll Configs ──────────────────────────────────────────────────────
    path(
        "payroll-configs/",
        PayrollConfigurationListCreateAPIView.as_view(),
        name="payroll-config-list-create",
    ),
    path(
        "payroll-configs/apply-template/",
        PayrollConfigurationApplyTemplateAPIView.as_view(),
        name="payroll-config-apply-template",
    ),
    path(
        "payroll-configs/<int:pk>/",
        PayrollConfigurationDetailAPIView.as_view(),
        name="payroll-config-detail",
    ),
    # ── Super Admin ──────────────────────────────────────────────────────────
    path(
        "super-admin/stats/", SuperAdminStatsAPIView.as_view(), name="super-admin-stats"
    ),
]
