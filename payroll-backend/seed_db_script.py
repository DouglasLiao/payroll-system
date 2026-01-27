import os
import django
import random
from datetime import date, timedelta
from decimal import Decimal

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from site_manage.models import (
    Company,
    User,
    Provider,
    Payroll,
    PayrollStatus,
    UserRole,
    PaymentMethod,
)
from django.utils import timezone


def date_range(start_date, end_date):
    """Generate months between start and end date"""
    curr_date = start_date
    while curr_date <= end_date:
        yield curr_date
        # Move to next month
        if curr_date.month == 12:
            curr_date = date(curr_date.year + 1, 1, 1)
        else:
            curr_date = date(curr_date.year, curr_date.month + 1, 1)


def main():
    print("WARNING: This will delete all existing data!")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    if confirm not in ["yes", "y"]:
        print("Aborted.")
        return

    print("Cleaning database...")
    Payroll.objects.all().delete()
    Provider.objects.all().delete()
    User.objects.all().delete()
    Company.objects.all().delete()

    print("Creating Company...")
    company = Company.objects.create(
        name="Tech Solutions Ltda",
        cnpj="12.345.678/0001-90",
        email="contact@techsolutions.com",
        phone="(11) 98765-4321",
    )

    print("Creating Admin User...")
    User.objects.create_user(
        username="admin",
        email="admin@techsolutions.com",
        password="password123",
        role=UserRole.CUSTOMER_ADMIN,
        company=company,
        first_name="Admin",
        last_name="User",
    )

    print(f"Creating 50 Providers...")
    providers = []

    first_names = [
        "Ana",
        "Bruno",
        "Carlos",
        "Daniela",
        "Eduardo",
        "Fernanda",
        "Gabriel",
        "Helena",
        "Igor",
        "Julia",
        "Lucas",
        "Mariana",
        "Nicolas",
        "Olivia",
        "Pedro",
        "Rafael",
        "Sofia",
        "Thiago",
        "Vitoria",
        "Wagner",
    ]
    last_names = [
        "Silva",
        "Santos",
        "Oliveira",
        "Souza",
        "Rodrigues",
        "Ferreira",
        "Almeida",
        "Costa",
        "Gomes",
        "Martins",
        "Pereira",
        "Barbosa",
        "Lima",
        "Araujo",
        "Ribeiro",
    ]
    roles = [
        "Developer",
        "Designer",
        "Manager",
        "QA Engineer",
        "DevOps",
        "Product Owner",
    ]

    for i in range(50):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        role = random.choice(roles)
        monthly_value = Decimal(random.randint(5000, 15000))

        provider = Provider.objects.create(
            name=name,
            role=role,
            monthly_value=monthly_value,
            monthly_hours=168,
            advance_enabled=True,
            advance_percentage=Decimal("40.00"),
            payment_method=PaymentMethod.PIX,
            company=company,
            email=f"{name.lower().replace(' ', '.')}@example.com",
            description=f"Consultor {role}",
        )
        providers.append(provider)

    print("Generating Monthly Payrolls (2021-2026)...")
    start_date = date(2021, 1, 1)
    end_date = date(2026, 1, 1)

    total_payrolls = 0

    for provider in providers:
        for month_date in date_range(start_date, end_date):
            ref_month = month_date.strftime("%m/%Y")

            # Random variations
            overtime = (
                Decimal(random.randint(0, 10)) if random.random() > 0.7 else Decimal(0)
            )

            # Determine status with distribution:
            # 70% PAID, 20% CLOSED, 10% DRAFT
            rand = random.random()
            if rand < 0.70:
                status = PayrollStatus.PAID
                # PAID: Both closed_at and paid_at are set
                # Use reference month to create realistic timestamps
                year, month = map(int, ref_month.split("/")[::-1])
                # Closing date: last day of the month
                closed_date = timezone.make_aware(
                    timezone.datetime(year, month, 28) + timedelta(days=4)
                ) - timedelta(
                    days=(timezone.datetime(year, month, 28) + timedelta(days=4)).day
                )
                # Payment date: ~5 days after closing
                paid_date = closed_date + timedelta(days=random.randint(3, 7))

                payroll_kwargs = {
                    "status": status,
                    "closed_at": closed_date,
                    "paid_at": paid_date,
                }
            elif rand < 0.90:
                status = PayrollStatus.CLOSED
                # CLOSED: Only closed_at is set
                year, month = map(int, ref_month.split("/")[::-1])
                closed_date = timezone.make_aware(
                    timezone.datetime(year, month, 28) + timedelta(days=4)
                ) - timedelta(
                    days=(timezone.datetime(year, month, 28) + timedelta(days=4)).day
                )

                payroll_kwargs = {
                    "status": status,
                    "closed_at": closed_date,
                    "paid_at": None,
                }
            else:
                status = PayrollStatus.DRAFT
                # DRAFT: No timestamps
                payroll_kwargs = {
                    "status": status,
                    "closed_at": None,
                    "paid_at": None,
                }

            # Create Payroll (auto-calculation happens on save)
            Payroll.objects.create(
                provider=provider,
                reference_month=ref_month,
                base_value=provider.monthly_value,
                overtime_hours_50=overtime,
                **payroll_kwargs,
            )
            total_payrolls += 1

        print(f"  - Generated history for {provider.name}")

    print(
        f"Done! Created {len(providers)} providers and {total_payrolls} payroll records."
    )


if __name__ == "__main__":
    main()
