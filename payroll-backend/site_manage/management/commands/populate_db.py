"""
Comando Django para popular o banco de dados com dados de teste.

Recria o ambiente de testes com:
- Empresas (Super Admin, Cliente, Dummy)
- Usuários (Super Admin, Customer Admin)
- Prestadores
- Folhas de Pagamento (histórico 2025-2026)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random
from datetime import date, timedelta

from site_manage.models import (
    Provider,
    Payroll,
    PayrollStatus,
    PayrollConfiguration,
)
from users.models import (
    Company,
    User,
    UserRole,
    Subscription,
    PlanType,
)
from site_manage.services.payroll_service import PayrollService


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


class Command(BaseCommand):
    help = "Popula o banco de dados com dados fictícios de prestadores e folhas de pagamento"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Cleaning database..."))

        try:
            Payroll.objects.all().delete()
            self.stdout.write("  ✓ Payrolls deleted")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ⚠ Payrolls: {e}"))

        try:
            Provider.objects.all().delete()
            self.stdout.write("  ✓ Providers deleted")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ⚠ Providers: {e}"))

        try:
            User.objects.all().delete()
            self.stdout.write("  ✓ Users deleted")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ⚠ Users: {e}"))

        try:
            PayrollConfiguration.objects.all().delete()
            self.stdout.write("  ✓ PayrollConfiguration deleted")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ⚠ PayrollConfiguration: {e}"))

        try:
            Subscription.objects.all().delete()
            self.stdout.write("  ✓ Subscription deleted")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ⚠ Subscription: {e}"))

        try:
            Company.objects.all().delete()
            self.stdout.write("  ✓ Companies deleted")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ⚠ Companies: {e}"))

        # ==============================================================================
        # 1. SUPER ADMIN COMPANY (ID=1)
        # ==============================================================================
        self.stdout.write("\nCreating Super Admin Company (ID=1)...")
        sa_company = Company.objects.create(
            name="Payroll System Admin",
            cnpj="00.000.000/0001-00",
            email="admin@payrollsystem.com",
            phone="(11) 0000-0000",
            is_active=True,
        )

        PayrollConfiguration.objects.create(company=sa_company)

        _sa_defaults = Subscription.get_plan_defaults(PlanType.UNLIMITED)
        Subscription.objects.create(
            company=sa_company,
            plan_type=PlanType.UNLIMITED,
            max_providers=_sa_defaults["max_providers"],
            price=_sa_defaults["price"],
            start_date=timezone.now().date(),
            is_active=True,
        )

        self.stdout.write("Creating Super Admin User...")
        User.objects.create_superuser(
            username="admin",
            email="admin@payrollsystem.com",
            password="password123",
            role=UserRole.SUPER_ADMIN,
            company=sa_company,
            first_name="Super",
            last_name="Admin",
        )

        self.stdout.write("Creating Extra Super Admins (Douglas & Bernardo)...")
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
        self.stdout.write("\nCreating Client Company (ID=2)...")
        client_company = Company.objects.create(
            name="Tech Solutions Ltda",
            cnpj="12.345.678/0001-90",
            email="contact@techsolutions.com",
            phone="(11) 98765-4321",
            is_active=True,
        )

        PayrollConfiguration.objects.create(company=client_company)

        _pro_defaults = Subscription.get_plan_defaults(PlanType.PRO)
        Subscription.objects.create(
            company=client_company,
            plan_type=PlanType.PRO,
            max_providers=_pro_defaults["max_providers"],
            price=_pro_defaults["price"],
            start_date=timezone.now().date(),
            is_active=True,
        )

        self.stdout.write("Creating Customer Admin User...")
        User.objects.create_user(
            username="tech_admin",
            email="admin@techsolutions.com",
            password="password123",
            role=UserRole.CUSTOMER_ADMIN,
            company=client_company,
            first_name="Tech",
            last_name="Admin",
        )

        # ==============================================================================
        # 2.5 DUMMY COMPANIES
        # ==============================================================================
        self.stdout.write("\nCreating 50 Dummy Companies...")
        for i in range(1, 51):
            dummy_company = Company.objects.create(
                name=f"Company {i}",
                cnpj=f"{i:02d}.000.000/0001-{i:02d}",
                email=f"contact@company{i}.com",
                phone=f"(11) 90000-{i:04d}",
                is_active=True,
            )
            PayrollConfiguration.objects.create(company=dummy_company)
            _basic_defaults = Subscription.get_plan_defaults(PlanType.BASIC)
            Subscription.objects.create(
                company=dummy_company,
                plan_type=PlanType.BASIC,
                max_providers=_basic_defaults["max_providers"],
                price=_basic_defaults["price"],
                start_date=timezone.now().date(),
                is_active=True,
                end_date=timezone.now().date() + timedelta(days=365),
            )

        # ==============================================================================
        # 3. PROVIDERS & PAYROLLS
        # ==============================================================================
        self.stdout.write(f"\nCreating 50 Providers for {client_company.name}...")
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

        def generate_cpf():
            cpf = [random.randint(0, 9) for _ in range(9)]
            for _ in range(2):
                val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
                cpf.append(11 - val if val > 1 else 0)
            return "%s%s%s.%s%s%s.%s%s%s-%s%s" % tuple(cpf)

        for i in range(50):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            role = random.choice(roles)
            monthly_value = Decimal(random.randint(5000, 15000))

            vt_enabled = random.random() < 0.7
            vt_trips = random.choices([2, 4, 6, 8], weights=[15, 60, 20, 5])[0]

            provider = Provider.objects.create(
                name=name,
                document=generate_cpf(),
                role=role,
                monthly_value=monthly_value,
                monthly_hours=168,
                advance_enabled=True,
                advance_percentage=Decimal("40.00"),
                vt_enabled=vt_enabled,
                vt_fare=Decimal("4.60"),
                vt_trips_per_day=vt_trips,
                payment_method=random.choice(["PIX", "TED", "TRANSFER"]),
                pix_key=f"+5591{random.randint(900000000, 999999999)}",
                company=client_company,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                description=f"Consultor {role}",
            )
            providers.append(provider)

        self.stdout.write(
            "Generating Monthly Payrolls (2025-2026) via PayrollService..."
        )
        start_date = date(2025, 1, 1)
        end_date = date(2026, 2, 1)

        service = PayrollService()
        total_payrolls = 0
        skipped = 0

        for provider in providers:
            for month_date in date_range(start_date, end_date):
                ref_month = month_date.strftime("%m/%Y")

                overtime_50 = (
                    Decimal(random.randint(1, 20))
                    if random.random() > 0.7
                    else Decimal(0)
                )
                holiday_hours = (
                    Decimal(random.randint(4, 12))
                    if random.random() > 0.9
                    else Decimal(0)
                )
                night_hours = (
                    Decimal(random.randint(8, 40))
                    if random.random() > 0.8
                    else Decimal(0)
                )
                late_minutes = random.randint(5, 120) if random.random() > 0.75 else 0

                has_absence = random.random() > 0.85
                absence_days = random.choice([1, 2]) if has_absence else 0
                absence_hours = Decimal(absence_days * 8)

                manual_discounts = (
                    Decimal(random.randint(50, 500))
                    if random.random() > 0.9
                    else Decimal(0)
                )

                try:
                    payroll = service.create_payroll(
                        provider_id=provider.id,
                        reference_month=ref_month,
                        overtime_hours_50=overtime_50,
                        holiday_hours=holiday_hours,
                        night_hours=night_hours,
                        late_minutes=late_minutes,
                        absence_days=absence_days,
                        absence_hours=absence_hours,
                        manual_discounts=manual_discounts,
                    )
                except ValueError:
                    skipped += 1
                    continue

                rand = random.random()
                year, month = int(ref_month[3:]), int(ref_month[:2])
                is_future = date(year, month, 1) > timezone.now().date()

                if rand < 0.70 and not is_future:
                    # PAID
                    if month == 12:
                        next_month = date(year + 1, 1, 1)
                    else:
                        next_month = date(year, month + 1, 1)
                    last_day = next_month - timedelta(days=1)
                    closed_dt = timezone.make_aware(
                        timezone.datetime(year, month, last_day.day) + timedelta(days=4)
                    )
                    paid_dt = closed_dt + timedelta(days=random.randint(1, 3))
                    Payroll.objects.filter(pk=payroll.pk).update(
                        status=PayrollStatus.PAID, closed_at=closed_dt, paid_at=paid_dt
                    )
                elif rand < 0.90 and not is_future:
                    # CLOSED
                    if month == 12:
                        next_month = date(year + 1, 1, 1)
                    else:
                        next_month = date(year, month + 1, 1)
                    last_day = next_month - timedelta(days=1)
                    closed_dt = timezone.make_aware(
                        timezone.datetime(year, month, last_day.day) + timedelta(days=4)
                    )
                    Payroll.objects.filter(pk=payroll.pk).update(
                        status=PayrollStatus.CLOSED, closed_at=closed_dt, paid_at=None
                    )

                total_payrolls += 1

        if skipped:
            self.stdout.write(self.style.WARNING(f"  ⚠ {skipped} payrolls skipped"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created {len(providers)} providers and {total_payrolls} payroll records."
            )
        )
        self.stdout.write("User Credentials:")
        self.stdout.write("  Super Admin: admin / password123 (Company ID: 1)")
        self.stdout.write("  Customer Admin: tech_admin / password123 (Company ID: 2)")
