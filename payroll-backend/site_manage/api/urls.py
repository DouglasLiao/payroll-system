"""
site_manage/urls.py — Payroll domain routes.

Auth, companies, subscriptions, and config routes have moved to users/urls.py.

Routes:
  GET/POST/PUT/PATCH/DELETE  /payrolls/                   → PayrollViewSet
  POST                       /payrolls/calculate/          → PayrollViewSet.calculate
  POST                       /payrolls/{id}/close/         → PayrollViewSet.close_payroll
  POST                       /payrolls/{id}/mark-as-paid/  → PayrollViewSet.mark_as_paid
  POST                       /payrolls/{id}/reopen/        → PayrollViewSet.reopen_payroll
  GET                        /payrolls/{id}/export-file/   → PayrollViewSet.export_file
  GET                        /payrolls/monthly-report/     → PayrollViewSet.monthly_report
  POST                       /payrolls/email-report/       → PayrollViewSet.email_report
  GET                        /payrolls/stats/              → PayrollViewSet.stats

  GET/POST/PUT/PATCH/DELETE  /providers/                   → ProviderViewSet

  GET                        /dashboard/                   → DashboardView
  GET                        /receipt/<pk>/                → generate_receipt
"""

from django.urls import path

from .views import (
    DashboardView,
    generate_receipt,
    ProviderListCreateAPIView,
    ProviderDetailAPIView,
    PayrollListAPIView,
    PayrollDetailAPIView,
    PayrollCalculateAPIView,
    PayrollCloseAPIView,
    PayrollMarkPaidAPIView,
    PayrollReopenAPIView,
    PayrollExportFileAPIView,
    PayrollMonthlyReportAPIView,
    PayrollEmailReportAPIView,
    PayrollStatsAPIView,
)

urlpatterns = [
    # Providers
    path(
        "providers/", ProviderListCreateAPIView.as_view(), name="provider-list-create"
    ),
    path(
        "providers/<int:pk>/", ProviderDetailAPIView.as_view(), name="provider-detail"
    ),
    # Payrolls - Actions
    path(
        "payrolls/calculate/",
        PayrollCalculateAPIView.as_view(),
        name="payroll-calculate",
    ),
    path(
        "payrolls/monthly-report/",
        PayrollMonthlyReportAPIView.as_view(),
        name="payroll-monthly-report",
    ),
    path(
        "payrolls/email-report/",
        PayrollEmailReportAPIView.as_view(),
        name="payroll-email-report",
    ),
    path("payrolls/stats/", PayrollStatsAPIView.as_view(), name="payroll-stats"),
    # Payrolls - Detail Actions
    path(
        "payrolls/<int:pk>/close/", PayrollCloseAPIView.as_view(), name="payroll-close"
    ),
    path(
        "payrolls/<int:pk>/mark-as-paid/",
        PayrollMarkPaidAPIView.as_view(),
        name="payroll-mark-paid",
    ),
    path(
        "payrolls/<int:pk>/reopen/",
        PayrollReopenAPIView.as_view(),
        name="payroll-reopen",
    ),
    path(
        "payrolls/<int:pk>/export-file/",
        PayrollExportFileAPIView.as_view(),
        name="payroll-export-file",
    ),
    # Payrolls - Core
    path("payrolls/", PayrollListAPIView.as_view(), name="payroll-list"),
    path("payrolls/<int:pk>/", PayrollDetailAPIView.as_view(), name="payroll-detail"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("receipt/<int:pk>/", generate_receipt, name="download-receipt"),
]
