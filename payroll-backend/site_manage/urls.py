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

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardView,
    PayrollViewSet,
    ProviderViewSet,
    generate_receipt,
)

router = DefaultRouter()
router.register(r"payrolls", PayrollViewSet, basename="payroll")
router.register(r"providers", ProviderViewSet, basename="provider")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("receipt/<int:pk>/", generate_receipt, name="download-receipt"),
]
