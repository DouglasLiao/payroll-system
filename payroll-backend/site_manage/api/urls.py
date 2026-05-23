"""
site_manage/urls.py — Payroll domain routes.
"""

from django.urls import path

from .views import (
    AcceptInviteAPIView,
    DashboardView,
    PayrollCalculateAPIView,
    PayrollCloseAPIView,
    PayrollDetailAPIView,
    PayrollEmailReportAPIView,
    PayrollExportFileAPIView,
    PayrollListAPIView,
    PayrollMarkPaidAPIView,
    PayrollMonthlyReportAPIView,
    PayrollReopenAPIView,
    PayrollStatsAPIView,
    ProviderDetailAPIView,
    ProviderListCreateAPIView,
    ScheduleSummaryAPIView,
    TimeAdjustmentRequestListCreateAPIView,
    TimeRecordListCreateAPIView,
    generate_receipt,
)

urlpatterns = [
    # Providers
    path("providers/", ProviderListCreateAPIView.as_view(), name="provider-list-create"),
    path("providers/<int:pk>/", ProviderDetailAPIView.as_view(), name="provider-detail"),

    # Onboarding / Invite
    path("accept-invite/", AcceptInviteAPIView.as_view(), name="accept-invite"),

    # Payrolls - Actions
    path("payrolls/calculate/", PayrollCalculateAPIView.as_view(), name="payroll-calculate"),
    path("payrolls/monthly-report/", PayrollMonthlyReportAPIView.as_view(), name="payroll-monthly-report"),
    path("payrolls/email-report/", PayrollEmailReportAPIView.as_view(), name="payroll-email-report"),
    path("payrolls/stats/", PayrollStatsAPIView.as_view(), name="payroll-stats"),

    # Payrolls - Detail Actions
    path("payrolls/<int:pk>/close/", PayrollCloseAPIView.as_view(), name="payroll-close"),
    path("payrolls/<int:pk>/mark-as-paid/", PayrollMarkPaidAPIView.as_view(), name="payroll-mark-paid"),
    path("payrolls/<int:pk>/reopen/", PayrollReopenAPIView.as_view(), name="payroll-reopen"),
    path("payrolls/<int:pk>/export-file/", PayrollExportFileAPIView.as_view(), name="payroll-export-file"),

    # Payrolls - Core
    path("payrolls/", PayrollListAPIView.as_view(), name="payroll-list"),
    path("payrolls/<int:pk>/", PayrollDetailAPIView.as_view(), name="payroll-detail"),

    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("receipt/<int:pk>/", generate_receipt, name="download-receipt"),

    # Time Tracking
    path("time-records/", TimeRecordListCreateAPIView.as_view(), name="time-record-list-create"),
    path("time-adjustments/", TimeAdjustmentRequestListCreateAPIView.as_view(), name="time-adjustment-list-create"),
    path("time-adjustments/<int:pk>/", TimeAdjustmentRequestListCreateAPIView.as_view(), name="time-adjustment-detail"),
    path("schedule-summary/", ScheduleSummaryAPIView.as_view(), name="schedule-summary"),
]
