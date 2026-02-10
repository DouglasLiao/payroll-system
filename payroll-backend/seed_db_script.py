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
    PayrollConfiguration,
    Subscription,
    PlanType,
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
    # confirm = input("Are you sure? (yes/no): ").strip().lower()
    # if confirm not in ["yes", "y"]:
    #     print("Aborted.")
    #     return

    print("Cleaning database...")

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
        PayrollConfiguration.objects.all().delete()
        print("  ✓ PayrollConfiguration deleted")
    except Exception as e:
        print(f"  ⚠ PayrollConfiguration: {e}")

    try:
        Subscription.objects.all().delete()
        print("  ✓ Subscription deleted")
    except Exception as e:
        print(f"  ⚠ Subscription: {e}")

    try:
        Company.objects.all().delete()
        print("  ✓ Companies deleted")
    except Exception as e:
        print(f"  ⚠ Companies: {e}")

    # ==============================================================================
    # 1. SUPER ADMIN COMPANY (ID=1)
    # ==============================================================================
    print("\nCreating Super Admin Company (ID=1)...")
    sa_company = Company.objects.create(
        id=1,
        name="Payroll System Admin",
        cnpj="00.000.000/0001-00",
        email="admin@payrollsystem.com",
        phone="(11) 0000-0000",
        is_active=True,
    )

    # Create Config for SA Company
    PayrollConfiguration.objects.create(company=sa_company)

    # Create Subscription for SA Company
    Subscription.objects.create(
        company=sa_company,
        plan_type=PlanType.UNLIMITED,
        start_date=timezone.now().date(),
        is_active=True,
    )

    print("Creating Super Admin User...")
    User.objects.create_superuser(
        username="admin",
        email="admin@payrollsystem.com",
        password="password123",
        role=UserRole.SUPER_ADMIN,
        company=sa_company,  # Linked to ID 1
        first_name="Super",
        last_name="Admin",
    )

    print("Creating Extra Super Admins (Douglas & Bernardo)...")
    User.objects.create_superuser(
        username="douglas",
        email="douglas@payrollsystem.com",
        password="password123",
        role=UserRole.SUPER_ADMIN,
        company=sa_company,
        first_name="Douglas",
        last_name="Liao",
    )
    User.objects.create_superuser(
        username="bernardo",
        email="bernardo@payrollsystem.com",
        password="password123",
        role=UserRole.SUPER_ADMIN,
        company=sa_company,
        first_name="Bernardo",
        last_name="Silva",
    )

    # ==============================================================================
    # 2. CLIENT COMPANY (ID=2)
    # ==============================================================================
    print("\nCreating Client Company (ID=2)...")
    client_company = Company.objects.create(
        id=2,
        name="Tech Solutions Ltda",
        cnpj="12.345.678/0001-90",
        email="contact@techsolutions.com",
        phone="(11) 98765-4321",
        is_active=True,
    )

    # Create Config for Client Company
    PayrollConfiguration.objects.create(company=client_company)

    # Create Subscription for Client Company
    Subscription.objects.create(
        company=client_company,
        plan_type=PlanType.PRO,
        start_date=timezone.now().date(),
        is_active=True,
    )

    print("Creating Customer Admin User...")
    User.objects.create_user(
        username="tech_admin",
        email="admin@techsolutions.com",
        password="password123",  # standard password
        role=UserRole.CUSTOMER_ADMIN,
        company=client_company,  # Linked to ID 2
        first_name="Tech",
        last_name="Admin",
    )

    # ==============================================================================
    # 3. PROVIDERS & PAYROLLS (FOR CLIENT COMPANY)
    # ==============================================================================
    print(f"\nCreating 50 Providers for {client_company.name}...")
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
        "Developer",
        "Designer",
        "Product Manager",
        "QA Engineer",
        "DevOps",
        "Data Scientist",
        "System Architect",
        "Tech Lead",
        "Scrum Master",
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
            company=client_company,  # Linked to ID 2
            email=f"{name.lower().replace(' ', '.')}@example.com",
            description=f"Consultor {role}",
        )
        # Create user for provider access (optional, but good for completeness)
        # We skip creating users for ALL providers to avoid clutter, maybe just a few?
        # provider.user = User.objects.create_user(...)
        # For now, keep it simple.

        providers.append(provider)

    print("Generating Monthly Payrolls (2025-2026)...")
    start_date = date(2025, 1, 1)  # Reduce range for speed
    end_date = date(2026, 2, 1)

    total_payrolls = 0

    for provider in providers:
        for month_date in date_range(start_date, end_date):
            ref_month = month_date.strftime("%m/%Y")

            # Random variations
            overtime_50 = (
                Decimal(random.randint(1, 20)) if random.random() > 0.7 else Decimal(0)
            )
            holiday_hours = (
                Decimal(random.randint(4, 12)) if random.random() > 0.9 else Decimal(0)
            )
            night_hours = (
                Decimal(random.randint(8, 40)) if random.random() > 0.8 else Decimal(0)
            )
            late_minutes = random.randint(5, 120) if random.random() > 0.75 else 0

            has_absence = random.random() > 0.85
            if has_absence:
                absence_days = Decimal(random.choice([0.5, 1, 1.5, 2]))
                absence_hours = absence_days * Decimal(8)
            else:
                absence_days = Decimal(0)
                absence_hours = Decimal(0)

            manual_discounts = (
                Decimal(random.randint(50, 500))
                if random.random() > 0.9
                else Decimal(0)
            )

            # Determine status
            rand = random.random()
            if rand < 0.70:
                status = PayrollStatus.PAID
                year, month = map(int, ref_month.split("/")[::-1])
                # Safety check for future dates vs current date
                if date(year, month, 1) > timezone.now().date():
                    status = PayrollStatus.DRAFT
                    closed_date = None
                    paid_date = None
                else:
                    # Closing date: last day of the month
                    # Note: Simplified date logic
                    if month == 12:
                        next_month = date(year + 1, 1, 1)
                    else:
                        next_month = date(year, month + 1, 1)
                    last_day_month = next_month - timedelta(days=1)

                    closed_date = timezone.make_aware(
                        timezone.datetime(year, month, last_day_month.day)
                        + timedelta(days=4)
                    )
                    paid_date = closed_date + timedelta(days=random.randint(1, 3))

                    payroll_kwargs = {
                        "status": status,
                        "closed_at": closed_date,
                        "paid_at": paid_date,
                    }
            elif rand < 0.90:
                status = PayrollStatus.CLOSED
                year, month = map(int, ref_month.split("/")[::-1])
                if date(year, month, 1) > timezone.now().date():
                    status = PayrollStatus.DRAFT
                    closed_date = None
                    paid_date = None
                else:
                    if month == 12:
                        next_month = date(year + 1, 1, 1)
                    else:
                        next_month = date(year, month + 1, 1)
                    last_day_month = next_month - timedelta(days=1)

                    closed_date = timezone.make_aware(
                        timezone.datetime(year, month, last_day_month.day)
                        + timedelta(days=4)
                    )
                    payroll_kwargs = {
                        "status": status,
                        "closed_at": closed_date,
                        "paid_at": None,
                    }
            else:
                status = PayrollStatus.DRAFT
                payroll_kwargs = {
                    "status": status,
                    "closed_at": None,
                    "paid_at": None,
                }

            if status == PayrollStatus.DRAFT:  # Safety override
                payroll_kwargs = {
                    "status": status,
                    "closed_at": None,
                    "paid_at": None,
                }

            # Create Payroll
            Payroll.objects.create(
                provider=provider,
                reference_month=ref_month,
                base_value=provider.monthly_value,
                overtime_hours_50=overtime_50,
                holiday_hours=holiday_hours,
                night_hours=night_hours,
                late_minutes=late_minutes,
                absence_hours=absence_hours,
                absence_days=absence_days,
                manual_discounts=manual_discounts,
                **payroll_kwargs,
            )
            total_payrolls += 1

    print(
        f"Done! Created {len(providers)} providers and {total_payrolls} payroll records."
    )
    print("User Credentials:")
    print("  Super Admin: admin / password123 (Company ID: 1)")
    print("  Customer Admin: tech_admin / password123 (Company ID: 2)")


if __name__ == "__main__":
    main()
