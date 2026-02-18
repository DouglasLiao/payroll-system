"""
Selectors — Camada de Consulta ao Banco de Dados

Seguindo o Django-Styleguide, este módulo centraliza todas as queries
complexas ao banco de dados, separando-as das views e dos services.

Regras:
- Selectors são funções que LEEM dados (SELECT)
- Services são funções que ESCREVEM dados (INSERT/UPDATE/DELETE)
- Views apenas orquestram: chamam selectors/services e serializam respostas
"""

from django.db.models import QuerySet, Sum, Count, Q, Avg
from django.db.models.functions import TruncMonth
from decimal import Decimal
from typing import Optional
from django.utils import timezone

from site_manage.models import (
    Company,
    PayrollConfiguration,
    PayrollMathTemplate,
    Provider,
    Payroll,
    PayrollStatus,
    Subscription,
    User,
    UserRole,
)


# ==============================================================================
# PAYROLL SELECTORS
# ==============================================================================


def payroll_list_for_user(*, user: User) -> QuerySet:
    """
    Retorna o queryset de folhas filtrado pelo papel do usuário.

    - SUPER_ADMIN: todas as folhas
    - CUSTOMER_ADMIN: folhas da empresa do usuário
    - PROVIDER: apenas as folhas do próprio prestador

    Args:
        user: Usuário autenticado

    Returns:
        QuerySet de Payroll com select_related otimizado
    """
    base_qs = Payroll.objects.select_related("provider__company").prefetch_related(
        "items"
    )

    if user.role == "SUPER_ADMIN":
        return base_qs.all()

    if user.role == "CUSTOMER_ADMIN":
        return base_qs.filter(provider__company=user.company)

    if user.role == "PROVIDER":
        return base_qs.filter(provider__user=user)

    return Payroll.objects.none()


def payroll_get_by_id(*, payroll_id: int, user: User) -> Optional[Payroll]:
    """
    Retorna uma folha específica respeitando o escopo do usuário.

    Args:
        payroll_id: ID da folha
        user: Usuário autenticado

    Returns:
        Instância de Payroll ou None se não encontrada/sem permissão
    """
    qs = payroll_list_for_user(user=user)
    return (
        qs.filter(pk=payroll_id)
        .select_related("provider__company__payroll_config")
        .first()
    )


def payroll_filter(
    *,
    user: User,
    reference_month: Optional[str] = None,
    provider_id: Optional[int] = None,
    status: Optional[str] = None,
) -> QuerySet:
    """
    Filtra folhas com parâmetros opcionais.

    Args:
        user: Usuário autenticado (define o escopo base)
        reference_month: Filtro por mês (MM/YYYY)
        provider_id: Filtro por prestador
        status: Filtro por status (DRAFT, CLOSED, PAID)

    Returns:
        QuerySet filtrado
    """
    qs = payroll_list_for_user(user=user)

    if reference_month:
        qs = qs.filter(reference_month=reference_month)

    if provider_id:
        qs = qs.filter(provider_id=provider_id)

    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-created_at")


# ==============================================================================
# DASHBOARD SELECTORS
# ==============================================================================


def dashboard_stats_for_company(*, company: Company) -> dict:
    """
    Calcula as estatísticas do dashboard para uma empresa.

    Retorna a estrutura que o frontend espera em EnhancedDashboardStats.stats:
    {
        total_providers: int,
        payrolls: { total, draft, closed, paid },
        financial: { total_value, pending_value, paid_value, average_payroll },
    }
    """
    providers_qs = Provider.objects.filter(company=company)
    payrolls_qs = Payroll.objects.filter(provider__company=company)

    total_providers = providers_qs.count()
    total_payrolls = payrolls_qs.count()
    draft_payrolls = payrolls_qs.filter(status=PayrollStatus.DRAFT).count()
    closed_payrolls = payrolls_qs.filter(status=PayrollStatus.CLOSED).count()
    paid_payrolls = payrolls_qs.filter(status=PayrollStatus.PAID).count()

    total_value = payrolls_qs.aggregate(total=Sum("net_value"))["total"] or Decimal("0")
    paid_value = payrolls_qs.filter(status=PayrollStatus.PAID).aggregate(
        total=Sum("net_value")
    )["total"] or Decimal("0")
    pending_value = payrolls_qs.filter(
        status__in=[PayrollStatus.DRAFT, PayrollStatus.CLOSED]
    ).aggregate(total=Sum("net_value"))["total"] or Decimal("0")
    average_payroll = (
        (total_value / total_payrolls) if total_payrolls > 0 else Decimal("0")
    )

    return {
        "total_providers": total_providers,
        "payrolls": {
            "total": total_payrolls,
            "draft": draft_payrolls,
            "closed": closed_payrolls,
            "paid": paid_payrolls,
        },
        "financial": {
            "total_value": float(total_value),
            "pending_value": float(pending_value),
            "paid_value": float(paid_value),
            "average_payroll": float(average_payroll),
        },
    }


def dashboard_stats_for_super_admin() -> dict:
    """
    Estatísticas globais para o Super Admin.

    Returns:
        Dicionário com estatísticas de todas as empresas
    """
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(is_active=True).count()
    total_providers = Provider.objects.count()
    total_payrolls = Payroll.objects.count()

    total_net = Payroll.objects.aggregate(total=Sum("net_value"))["total"] or Decimal(
        "0"
    )
    total_paid = Payroll.objects.filter(status=PayrollStatus.PAID).aggregate(
        total=Sum("net_value")
    )["total"] or Decimal("0")

    active_subscriptions = Subscription.objects.filter(is_active=True).count()

    return {
        "companies": {
            "total": total_companies,
            "active": active_companies,
            "inactive": total_companies - active_companies,
        },
        "providers": {
            "total": total_providers,
        },
        "payrolls": {
            "total": total_payrolls,
            "total_net": total_net,
            "total_paid": total_paid,
        },
        "subscriptions": {
            "active": active_subscriptions,
        },
    }


# ==============================================================================
# PROVIDER SELECTORS
# ==============================================================================


def provider_list_for_user(*, user: User) -> QuerySet:
    """
    Retorna o queryset de prestadores filtrado pelo papel do usuário.

    Args:
        user: Usuário autenticado

    Returns:
        QuerySet de Provider
    """
    if user.role == "SUPER_ADMIN":
        return Provider.objects.select_related("company").all()

    if user.role == "CUSTOMER_ADMIN":
        return Provider.objects.filter(company=user.company).select_related("company")

    if user.role == "PROVIDER":
        return Provider.objects.filter(user=user).select_related("company")

    return Provider.objects.none()


def provider_get_by_id(*, provider_id: int, user: User) -> Optional[Provider]:
    """
    Retorna um prestador específico respeitando o escopo do usuário.

    Args:
        provider_id: ID do prestador
        user: Usuário autenticado

    Returns:
        Instância de Provider ou None
    """
    return provider_list_for_user(user=user).filter(pk=provider_id).first()


# ==============================================================================
# SUBSCRIPTION SELECTORS
# ==============================================================================


def subscription_get_active_for_company(*, company: Company) -> Optional[Subscription]:
    """
    Retorna a assinatura ativa de uma empresa.

    Args:
        company: Empresa

    Returns:
        Instância de Subscription ou None
    """
    return Subscription.objects.filter(company=company, is_active=True).first()


def subscription_can_add_provider(*, company: Company) -> bool:
    """
    Verifica se a empresa pode adicionar mais prestadores.

    Args:
        company: Empresa

    Returns:
        True se pode adicionar, False se atingiu o limite
    """
    subscription = subscription_get_active_for_company(company=company)
    if not subscription:
        return False

    current_count = Provider.objects.filter(company=company).count()
    return current_count < subscription.max_providers


# ==============================================================================
# USER SELECTORS
# ==============================================================================


def user_list_for_company(*, company: Company, role: Optional[str] = None) -> QuerySet:
    """
    Retorna usuários de uma empresa, opcionalmente filtrados por papel.

    Args:
        company: Empresa
        role: Papel do usuário (UserRole.CUSTOMER_ADMIN, etc.) — opcional

    Returns:
        QuerySet de User
    """
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
    """
    Retorna empresas com filtros opcionais.

    Args:
        is_active: Filtro por status ativo/inativo
        search: Filtro por nome ou CNPJ (case-insensitive)

    Returns:
        QuerySet de Company ordenado por nome
    """
    qs = Company.objects.all().order_by("name")
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(cnpj__icontains=search))
    return qs


# ==============================================================================
# SUPER ADMIN STATS SELECTOR
# ==============================================================================


def super_admin_stats() -> dict:
    """
    Calcula as estatísticas globais para o Dashboard do Super Admin.

    Centraliza todas as queries de agregação que antes estavam inline na view.

    Returns:
        Dicionário com estatísticas de todas as empresas
    """
    today = timezone.now().date()

    total_companies = Company.objects.count()
    total_providers = Provider.objects.count()
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


# ==============================================================================
# LOOKUP SELECTORS (get-by-id)
# ==============================================================================


def company_get_by_id(*, company_id) -> Optional[Company]:
    """
    Retorna uma empresa pelo ID ou None se não encontrada.
    Substitui get_object_or_404(Company, pk=...) nas views.
    """
    return Company.objects.filter(pk=company_id).first()


def math_template_get_by_id(*, template_id) -> Optional[PayrollMathTemplate]:
    """
    Retorna um PayrollMathTemplate pelo ID ou None se não encontrado.
    """
    return PayrollMathTemplate.objects.filter(pk=template_id).first()


def math_template_list() -> QuerySet:
    """
    Retorna todos os templates de cálculo ordenados por nome.
    """
    return PayrollMathTemplate.objects.all().order_by("name")


def payroll_config_list(*, company_id=None) -> QuerySet:
    """
    Retorna configurações de folha, opcionalmente filtradas por empresa.

    Args:
        company_id: ID da empresa (opcional)

    Returns:
        QuerySet de PayrollConfiguration
    """
    qs = PayrollConfiguration.objects.all()
    if company_id:
        qs = qs.filter(company_id=company_id)
    return qs


def subscription_list(*, company_id=None) -> QuerySet:
    """
    Retorna assinaturas, opcionalmente filtradas por empresa.

    Args:
        company_id: ID da empresa (opcional)

    Returns:
        QuerySet de Subscription ordenado por data de criação decrescente
    """
    qs = Subscription.objects.all().order_by("-created_at")
    if company_id:
        qs = qs.filter(company_id=company_id)
    return qs
