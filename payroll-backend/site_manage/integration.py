from site_manage.infrastructure.models import PayrollConfiguration, Provider


def create_default_payroll_config(*, company_id: int) -> None:
    """
    Função de integração para ser chamada por outros apps (ex: users)
    para garantir a criação de configuração padrão da folha ao registrar/aprovar a empresa.
    """
    PayrollConfiguration.objects.get_or_create(company_id=company_id)


def get_provider_count_for_company(*, company_id: int) -> int:
    return Provider.objects.filter(company_id=company_id).count()


def get_total_providers_for_super_admin() -> int:
    return Provider.objects.count()
