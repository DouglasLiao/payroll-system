from api.models import Payroll, Provider, PayrollStatus, Company
from decimal import Decimal
import random


def populate_recent_varied_data():
    print("🚀 Adding varied recent data for dashboard visual testing...")

    company = Company.objects.first()
    providers = Provider.objects.filter(company=company)

    # Months to enhance
    months = ["08/2025", "09/2025", "10/2025", "11/2025", "12/2025", "01/2026"]

    for month in months:
        print(f"  📅 Processing {month}...")
        # Ensure at least 5 of each status per month if possible

        # 1. Force some DRAFTs
        drafts = Payroll.objects.filter(
            reference_month=month, status=PayrollStatus.DRAFT
        ).count()
        if drafts < 5:
            needed = 5 - drafts
            candidates = Payroll.objects.filter(reference_month=month).exclude(
                status=PayrollStatus.DRAFT
            )[:needed]
            for p in candidates:
                p.status = PayrollStatus.DRAFT
                p.save()
                print(f"    - Converted {p} to DRAFT")

        # 2. Force some CLOSED
        closed = Payroll.objects.filter(
            reference_month=month, status=PayrollStatus.CLOSED
        ).count()
        if closed < 5:
            needed = 5 - closed
            candidates = Payroll.objects.filter(reference_month=month).exclude(
                status__in=[PayrollStatus.DRAFT, PayrollStatus.CLOSED]
            )[:needed]
            for p in candidates:
                p.status = PayrollStatus.CLOSED
                p.save()
                print(f"    - Converted {p} to CLOSED")

        # 3. Add some visual spikes (high value payrolls)
        high_rollers = providers.order_by("?")[:3]
        for provider in high_rollers:
            payroll, created = Payroll.objects.get_or_create(
                provider=provider,
                reference_month=month,
                defaults={
                    "base_value": Decimal("15000.00"),
                    "status": PayrollStatus.PAID,
                },
            )
            if not created:
                payroll.base_value = Decimal("25000.00")  # Spike
                payroll.overtime_hours_50 = Decimal("10.0")
                payroll.save()
                print(f"    - Boosted value for {payroll}")

    print("✅ Done adding variation.")


if __name__ == "__main__":
    populate_recent_varied_data()
