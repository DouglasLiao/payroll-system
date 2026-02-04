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

    # Safe cleanup - handles cases where tables might not exist yet
    try:
        Payroll.objects.all().delete()
        print("  ✓ Payrolls deleted")
    except Exception as e:
        print(f"  ⚠ Payrolls: {e}")

    try:
        Provider.objects.all().delete()
        print("  ✓ Providers deleted")
    except Exception as e:
        print(f"  ⚠ Providers: {e}")

    try:
        User.objects.all().delete()
        print("  ✓ Users deleted")
    except Exception as e:
        print(f"  ⚠ Users: {e}")

    try:
        Company.objects.all().delete()
        print("  ✓ Companies deleted")
    except Exception as e:
        print(f"  ⚠ Companies: {e}")

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
        "Joao",
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
        "Alberto",
        "Amanda",
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
        "Carneiro",
        "Freitas",
        "Araujo",
        "Ribeiro",
    ]
    roles = [
        "Servente",
        "Dentista",
        "Pedreiro",
        "Eletricista",
        "Encanador",
        "Pintor",
        "Carpinteiro",
        "Pedreiro",
        "Padeiro",
        "Cozinheiro",
        "Garçom",
        "Barman",
        "Atendente",
        "Caixa",
        "Repositor",
        "Empacotador",
        "Açougueiro",
        "Peixeiro",
        "Hortifruti",
        "Padaria",
        "Confeitaria",
        "Lanchonete",
        "Restaurante",
        "Bar",
        "Cafeteria",
        "Sorveteria",
        "Churrascaria",
        "Pizzaria",
        "Hamburgueria",
        "Temakeria",
    ]

    for i in range(50):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        role = random.choice(roles)
        monthly_value = Decimal(random.randint(5000, 15000))

        # VT configuration (70% dos providers têm VT habilitado)
        vt_enabled = random.random() < 0.7
        # Variedade de viagens: maioria usa 4, alguns 2 ou 6
        vt_trips = random.choices([2, 4, 6, 8], weights=[15, 60, 20, 5])[0]

        provider = Provider.objects.create(
            name=name,
            role=role,
            monthly_value=monthly_value,
            monthly_hours=168,
            advance_enabled=True,
            advance_percentage=Decimal("40.00"),
            vt_enabled=vt_enabled,
            vt_fare=Decimal("4.60"),  # Tarifa de Belém
            vt_trips_per_day=vt_trips,
            payment_method=random.choice(["PIX", "TED", "TRANSFER"]),
            pix_key=f"+5591{random.randint(900000000, 999999999)}",
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

            # Random variations - creating more realistic scenarios
            # 30% chance of having some overtime at 50%
            overtime_50 = (
                Decimal(random.randint(1, 20)) if random.random() > 0.7 else Decimal(0)
            )

            # 15% chance of having overtime at 100% (usually less than 50%)
            overtime_100 = (
                Decimal(random.randint(1, 10)) if random.random() > 0.85 else Decimal(0)
            )

            # 10% chance of working on holidays
            holiday_hours = (
                Decimal(random.randint(4, 12)) if random.random() > 0.9 else Decimal(0)
            )

            # 20% chance of night shift hours
            night_hours = (
                Decimal(random.randint(8, 40)) if random.random() > 0.8 else Decimal(0)
            )

            # 25% chance of being late (in minutes)
            late_minutes = random.randint(5, 120) if random.random() > 0.75 else 0

            # 15% chance of absences
            has_absence = random.random() > 0.85
            if has_absence:
                # Random between 0.5 to 3 days absent
                absence_days = Decimal(random.choice([0.5, 1, 1.5, 2, 2.5, 3]))
                # Calculate absence hours based on 8 hours per day
                absence_hours = absence_days * Decimal(8)
            else:
                absence_days = Decimal(0)
                absence_hours = Decimal(0)

            # 10% chance of manual discounts (penalties, loan deductions, etc)
            manual_discounts = (
                Decimal(random.randint(50, 500))
                if random.random() > 0.9
                else Decimal(0)
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
                overtime_hours_50=overtime_50,
                overtime_hours_100=overtime_100,
                holiday_hours=holiday_hours,
                night_hours=night_hours,
                late_minutes=late_minutes,
                absence_hours=absence_hours,
                absence_days=absence_days,
                manual_discounts=manual_discounts,
                **payroll_kwargs,
            )
            total_payrolls += 1

        print(f"  - Generated history for {provider.name}")

    print(
        f"Done! Created {len(providers)} providers and {total_payrolls} payroll records."
    )


if __name__ == "__main__":
    main()
