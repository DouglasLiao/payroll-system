"""
Selectors — Camada de Consulta ao Banco de Dados

Seguindo o Django-Styleguide, este módulo centraliza todas as queries
complexas ao banco de dados, separando-as das views e dos services.

Regras:
- Selectors são funções que LEEM dados (SELECT)
- Services são funções que ESCREVEM dados (INSERT/UPDATE/DELETE)
- Views apenas orquestram: chamam selectors/services e serializam respostas
"""

from django.db.models import QuerySet, Sum, Q
from decimal import Decimal
from typing import Optional
from django.utils import timezone

from site_manage.infrastructure.models import (
    PayrollConfiguration,
    PayrollMathTemplate,
    Provider,
    Payroll,
    PayrollStatus,
)
from users.models import User


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


def dashboard_stats_for_company(*, company_id: int) -> dict:
    """
    Calcula as estatísticas do dashboard para uma empresa.

    Retorna a estrutura que o frontend espera em EnhancedDashboardStats.stats:
    {
        total_providers: int,
        payrolls: { total, draft, closed, paid },
        financial: { total_value, pending_value, paid_value, average_payroll },
    }
    """
    providers_qs = Provider.objects.filter(company_id=company_id)
    payrolls_qs = Payroll.objects.filter(provider__company_id=company_id)

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
# LOOKUP SELECTORS (get-by-id)
# ==============================================================================


def math_template_get_by_id(*, template_id) -> Optional[PayrollMathTemplate]:
    """
    Retorna um PayrollMathTemplate pelo ID ou None se não encontrado.
    """
    return PayrollMathTemplate.objects.filter(pk=template_id).first()


def math_template_list() -> QuerySet:
    """
    Retorna todos os templates de cálculo ordenados por nome.
    Garante que o template Padrão exista antes de retornar.
    """
    default_template = PayrollMathTemplate.objects.filter(is_default=True).first()
    if not default_template:
        PayrollMathTemplate.objects.create(
            name="Padrão",
            description="Template padrão inalterável do sistema.",
            is_default=True,
            overtime_percentage=Decimal("50.00"),
            night_shift_percentage=Decimal("20.00"),
            holiday_percentage=Decimal("100.00"),
            advance_percentage=Decimal("40.00"),
        )
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
