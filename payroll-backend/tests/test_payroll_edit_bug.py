import os
import django
from decimal import Decimal

import sys

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from site_manage.models import Provider, Payroll, PayrollStatus, Company
from services.payroll_service import PayrollService


def setup_test_data():
    Payroll.objects.all().delete()
    Provider.objects.all().delete()
    Company.objects.all().delete()

    company = Company.objects.create(
        name="Test Company", cnpj="12345678000199", email="test@company.com"
    )

    provider1 = Provider.objects.create(
        name="Provider 1",
        role="Dev",
        monthly_value=Decimal("2000.00"),
        monthly_hours=220,
        company=company,
    )
    provider2 = Provider.objects.create(
        name="Provider 2",
        role="Dev",
        monthly_value=Decimal("3000.00"),
        monthly_hours=220,
        company=company,
    )
    return provider1, provider2


def test_duplicate_provider_update():
    print("\n" + "=" * 70)
    print("TEST: Update Payroll to Duplicate Provider")
    print("=" * 70)

    p1, p2 = setup_test_data()
    service = PayrollService()

    # Create payroll for P1 and P2 in the same month
    payroll1 = service.create_payroll(p1.id, "03/2026")
    payroll2 = service.create_payroll(p2.id, "03/2026")

    print(f"Created Payroll 1 for {p1.name} in 03/2026")
    print(f"Created Payroll 2 for {p2.name} in 03/2026")

    # Try to change Payroll 1's provider to P2 (should fail because P2 already has a payroll for 03/2026)
    print("Attempting to change Payroll 1 provider to Provider 2...")
    try:
        service.recalculate_payroll(payroll1.id, provider_id=p2.id)
        print("❌ FAILED: Succeeded but should have failed!")
        return False
    except ValueError as e:
        print(f"✅ SUCCESS: Caught expected error: {e}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Caught unexpected error: {type(e).__name__}: {e}")
        # If it's IntegrityError, it verifies the bug (crash instead of validation error)
        if "IntegrityError" in type(e).__name__:
            print("  -> verified bug: IntegrityError crash!")
        return False


if __name__ == "__main__":
    if test_duplicate_provider_update():
        exit(0)
    else:
        exit(1)
