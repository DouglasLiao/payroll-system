import os
import sys
from decimal import Decimal
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from site_manage.models import Provider, Payroll, PayrollStatus
from users.models import Company
from services.payroll_service import PayrollService


def reproduce_stale_payroll():
    print("=" * 60)
    print("🕵️  REPRODUÇÃO: FOLHA DESATUALIZADA APÓS EDIÇÃO DE PRESTADOR")
    print("=" * 60)

    # Setup
    company, _ = Company.objects.get_or_create(
        name="Stale Test Co",
        cnpj="88888888000188",
        defaults={"email": "stale@test.com"},
    )
    provider = Provider.objects.create(
        name="João Stale",
        monthly_value=Decimal("2000.00"),
        company=company,
        role="Tester",
    )

    service = PayrollService()

    # 1. Create Draft Payroll
    payroll = service.create_payroll(provider_id=provider.id, reference_month="10/2026")

    print(f"[1] Folha Criada (Draft). Valor Base: {payroll.base_value}")

    if payroll.base_value != Decimal("2000.00"):
        print("❌ Erro no setup: Valor base inicial incorreto.")
        return

    # 2. Update Provider Salary
    print(f"[2] Atualizando salário do prestador para R$ 3000.00...")
    provider.monthly_value = Decimal("3000.00")
    provider.save()

    # 3. Check Payroll Again (Reload from DB)
    payroll.refresh_from_db()
    print(f"[3] Verificando Folha (Draft) após update do prestador...")
    print(f"    - Valor Base na Folha: {payroll.base_value}")

    if payroll.base_value == Decimal("3000.00"):
        print("✅ A folha foi atualizada automaticamente!")
    else:
        print(f"❌ A folha NÃO foi atualizada. Valor ainda é {payroll.base_value}")
        print("   (Esperado: 3000.00)")


if __name__ == "__main__":
    reproduce_stale_payroll()
