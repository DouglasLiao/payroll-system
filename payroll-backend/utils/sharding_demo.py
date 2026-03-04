import os
import django
import sys
from decimal import Decimal

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from users.models import Company
from site_manage.models import Provider


def run_demo():
    print("--- Database Sharding Demo ---")

    # 1. Clear existing data for a clean demo
    # We delete from both to be sure
    Company.objects.using("default").all().delete()
    Company.objects.using("shard2").all().delete()

    # 2. Demonstration of Routing
    # Router logic in sharding_router.py:
    # even IDs -> 'default'
    # odd IDs -> 'shard2'

    print("\n[1] Creating Company Alpha (ID 2 - Target: 'default')...")
    c1 = Company(
        id=2, name="Company Alpha", cnpj="12345678000199", email="alpha@test.com"
    )
    c1.save()  # This triggers the router
    print(f"    Result: Company Alpha saved to DB: '{c1._state.db}'")

    print("\n[2] Creating Provider for Company Alpha...")
    p1 = Provider(
        company=c1,
        name="John Doe",
        monthly_value=Decimal("5000.00"),
        document="11122233344",
    )
    p1.save()
    print(f"    Result: Provider John Doe saved to DB: '{p1._state.db}'")

    print("\n" + "-" * 40)

    print("\n[3] Creating Company Beta (ID 3 - Target: 'shard2')...")
    c2 = Company(
        id=3, name="Company Beta", cnpj="98765432000188", email="beta@test.com"
    )
    c2.save()
    print(f"    Result: Company Beta saved to DB: '{c2._state.db}'")

    print("\n[4] Creating Provider for Company Beta...")
    p2 = Provider(
        company=c2,
        name="Jane Smith",
        monthly_value=Decimal("6000.00"),
        document="55566677788",
    )
    p2.save()
    print(f"    Result: Provider Jane Smith saved to DB: '{p2._state.db}'")

    print("\n" + "=" * 40)
    print("--- FINAL VERIFICATION (Cross-Database Count) ---")

    def get_counts(db_name):
        comp_count = Company.objects.using(db_name).count()
        prov_count = Provider.objects.using(db_name).count()
        return comp_count, prov_count

    def_comps, def_provs = get_counts("default")
    s2_comps, s2_provs = get_counts("shard2")

    print(f"Database 'default' contents: {def_comps} Companies, {def_provs} Providers")
    print(f"Database 'shard2'  contents: {s2_comps} Companies, {s2_provs} Providers")

    if def_comps == 1 and s2_comps == 1 and def_provs == 1 and s2_provs == 1:
        print(
            "\n✅ SUCCESS: Data was correctly routed to different shards based on Company ID!"
        )
    else:
        print("\n❌ FAILURE: Data routing did not behave as expected.")


if __name__ == "__main__":
    run_demo()
