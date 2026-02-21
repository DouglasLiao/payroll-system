from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from users.models import Company, Subscription, User


def get_super_admin_stats_integration() -> dict:
    """
    Exporta os dados estatísticos lidos do banco de dados do app users,
    para não engessar/acoplar o site_manage às entities diretamente.
    """
    today = timezone.now().date()

    total_companies = Company.objects.count()
    from site_manage.integration import get_total_providers_for_super_admin

    total_providers = get_total_providers_for_super_admin()

    active_subscriptions = Subscription.objects.filter(
        is_active=True, end_date__gte=today
    ).count()
    mrr = Subscription.objects.filter(is_active=True, end_date__gte=today).aggregate(
        total=Sum("price")
    )["total"] or Decimal("0.00")
    pending_approvals = Company.objects.filter(is_active=False).count()

    return {
        "total_companies": total_companies,
        "total_providers": total_providers,
        "active_subscriptions": active_subscriptions,
        "mrr": mrr,
        "pending_approvals": pending_approvals,
    }
