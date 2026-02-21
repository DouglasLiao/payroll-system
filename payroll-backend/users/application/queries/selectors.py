from decimal import Decimal
from typing import Optional

from django.db.models import Q, QuerySet, Sum
from django.utils import timezone

from site_manage.integration import get_provider_count_for_company
from users.integration import get_super_admin_stats_integration
from users.models import (
    Company,
    Subscription,
    User,
)

# ==============================================================================
# SUBSCRIPTION SELECTORS
# ==============================================================================


def subscription_get_active_for_company(*, company: Company) -> Optional[Subscription]:
    return Subscription.objects.filter(company=company, is_active=True).first()


def subscription_can_add_provider(*, company: Company) -> bool:
    subscription = subscription_get_active_for_company(company=company)
    if not subscription:
        return False

    current_count = get_provider_count_for_company(company_id=company.id)
    return current_count < subscription.max_providers


def subscription_list(*, company_id=None) -> QuerySet:
    qs = Subscription.objects.all().order_by("-created_at")
    if company_id:
        qs = qs.filter(company_id=company_id)
    return qs


# ==============================================================================
# USER SELECTORS
# ==============================================================================


def user_list_for_company(*, company: Company, role: Optional[str] = None) -> QuerySet:
    qs = User.objects.filter(company=company).order_by("username")
    if role:
        qs = qs.filter(role=role)
    return qs


# ==============================================================================
# COMPANY SELECTORS
# ==============================================================================


def company_list_filtered(
    *,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> QuerySet:
    qs = Company.objects.all().order_by("name")
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(cnpj__icontains=search))
    return qs


def company_get_by_id(*, company_id) -> Optional[Company]:
    return Company.objects.filter(pk=company_id).first()


# ==============================================================================
# SUPER ADMIN STATS
# ==============================================================================


def super_admin_stats() -> dict:
    return get_super_admin_stats_integration()
