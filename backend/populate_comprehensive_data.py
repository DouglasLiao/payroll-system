#!/usr/bin/env python
"""
Script para popular o banco de dados PostgreSQL com dados completos e realistas
- 1 empresa e 1 admin
- 50+ colaboradores (providers)
- Payrolls desde 01/2023 até hoje com dados variados
- CORRIGIDO: Agora usa os campos corretos do modelo Payroll (base_value, overtime_hours_50, etc.)
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from api.models import (
    Company,
    User,
    UserRole,
    Provider,
    Payroll,
    PaymentMethod,
    PayrollStatus,
)
from django.contrib.auth.hashers import make_password

# Dados para geração aleatória
FIRST_NAMES = [
    "João",
    "Maria",
    "Pedro",
    "Ana",
    "Carlos",
    "Julia",
    "Lucas",
    "Fernanda",
    "Rafael",
    "Beatriz",
    "Gabriel",
    "Camila",
    "Felipe",
    "Larissa",
    "Bruno",
    "Amanda",
    "Gustavo",
    "Patricia",
    "Diego",
    "Juliana",
    "Rodrigo",
    "Carla",
    "Thiago",
    "Aline",
    "Marcos",
    "Renata",
    "André",
    "Tatiana",
    "Ricardo",
    "Vanessa",
    "Paulo",
    "Mariana",
    "Eduardo",
    "Bianca",
    "Leonardo",
    "Priscila",
    "Daniel",
    "Natalia",
    "Vinicius",
    "Sabrina",
    "Henrique",
    "Daniela",
    "Caio",
    "Bruna",
    "Mateus",
    "Isabela",
    "Arthur",
    "Leticia",
    "Victor",
    "Carolina",
]

LAST_NAMES = [
    "Silva",
    "Santos",
    "Oliveira",
    "Souza",
    "Rodrigues",
    "Ferreira",
    "Alves",
    "Pereira",
    "Lima",
    "Gomes",
    "Costa",
    "Ribeiro",
    "Martins",
    "Carvalho",
    "Almeida",
    "Lopes",
    "Soares",
    "Fernandes",
    "Vieira",
    "Barbosa",
    "Rocha",
    "Reis",
    "Teixeira",
    "Moreira",
    "Correia",
    "Castro",
    "Araujo",
    "Monteiro",
]

ROLES = [
    "Desenvolvedor Full Stack",
    "Desenvolvedor Backend",
    "Desenvolvedor Frontend",
    "Designer UX/UI",
    "Product Owner",
    "Scrum Master",
    "QA Engineer",
    "DevOps Engineer",
    "Arquiteto de Software",
    "Analista de Dados",
    "Engenheiro de ML",
    "Tech Lead",
    "Gerente de Projetos",
    "Analista de BI",
    "Desenvolvedor Mobile",
    "DBA",
    "Analista de Segurança",
    "Support Engineer",
    "Sales Engineer",
    "Customer Success Manager",
]


def generate_cpf():
    """Gera um CPF fictício válido"""
    return f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"


def generate_provider_data():
    """Gera dados aleatórios para um provider"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,999)}@email.com"

    return {
        "name": full_name,
        "role": random.choice(ROLES),
        "email": email,
        "monthly_value": Decimal(
            random.choice(
                [
                    5000,
                    5500,
                    6000,
                    6500,
                    7000,
                    7500,
                    8000,
                    8500,
                    9000,
                    9500,
                    10000,
                    11000,
                    12000,
                    13000,
                    14000,
                    15000,
                    16000,
                    18000,
                    20000,
                ]
            )
        ),
        "monthly_hours": 160,
        "payment_method": random.choice(
            [PaymentMethod.PIX, PaymentMethod.TED, PaymentMethod.TRANSFER]
        ),
        "pix_key": email if random.choice([True, False]) else generate_cpf(),
        "bank_name": random.choice(
            ["Banco do Brasil", "Itaú", "Santander", "Bradesco", "Nubank", "Inter"]
        ),
        "bank_agency": f"{random.randint(1000,9999)}",
        "bank_account": f"{random.randint(10000,99999)}-{random.randint(0,9)}",
        "vt_value": Decimal(random.choice([0, 150, 200, 250, 300])),
        "advance_enabled": random.choice([True, False]),
        "advance_percentage": (
            Decimal(random.choice([0, 30, 40, 50]))
            if random.choice([True, False])
            else Decimal(0)
        ),
    }


def generate_months(start_year=2023, start_month=1):
    """Gera lista de meses desde start_year/start_month até agora"""
    months = []
    current_date = datetime.now()
    date = datetime(start_year, start_month, 1)

    while date <= current_date:
        months.append(date.strftime("%m/%Y"))
        # Próximo mês
        if date.month == 12:
            date = datetime(date.year + 1, 1, 1)
        else:
            date = datetime(date.year, date.month + 1, 1)

    return months


def create_payroll_for_provider(provider, reference_month, company):
    """Cria payroll com dados variados"""
    # Decidir status (mais recentes tendem a ser DRAFT ou CLOSED, antigos são PAID)
    month, year = reference_month.split("/")
    month_date = datetime(int(year), int(month), 1)
    months_old = (datetime.now().year - month_date.year) * 12 + (
        datetime.now().month - month_date.month
    )

    if months_old < 2:
        status = random.choice(
            [PayrollStatus.DRAFT, PayrollStatus.CLOSED, PayrollStatus.PAID]
        )
    elif months_old < 6:
        status = random.choice(
            [PayrollStatus.CLOSED, PayrollStatus.PAID, PayrollStatus.PAID]
        )
    else:
        status = PayrollStatus.PAID

    # Horas extras (algumas vezes)
    overtime_hours_50 = (
        Decimal(random.randint(0, 20)) if random.random() < 0.3 else Decimal(0)
    )

    # Feriados (ocasionalmente)
    holiday_hours = (
        Decimal(random.randint(0, 16)) if random.random() < 0.2 else Decimal(0)
    )

    # Horas noturnas (ocasionalmente)
    night_hours = (
        Decimal(random.randint(0, 12)) if random.random() < 0.15 else Decimal(0)
    )

    # Faltas (raramente)
    absence_hours = (
        Decimal(random.randint(0, 24)) if random.random() < 0.15 else Decimal(0)
    )

    # Atrasos (raramente)
    late_minutes = random.randint(0, 120) if random.random() < 0.1 else 0

    # Adiantamento
    advance_value = (
        (provider.monthly_value * provider.advance_percentage / Decimal(100))
        if provider.advance_enabled
        else Decimal(0)
    )

    # Criar payroll - o modelo calcula automaticamente os valores
    payroll = Payroll.objects.create(
        provider=provider,
        reference_month=reference_month,
        status=status,
        base_value=provider.monthly_value,
        advance_value=advance_value,
        overtime_hours_50=overtime_hours_50,
        holiday_hours=holiday_hours,
        night_hours=night_hours,
        absence_hours=absence_hours,
        late_minutes=late_minutes,
        vt_discount=provider.vt_value,
        manual_discounts=Decimal(0),
    )

    return payroll


def populate_comprehensive_data():
    """População completa de dados"""
    print("🚀 Iniciando população COMPLETA do banco de dados PostgreSQL...\n")

    # 1. Criar ou buscar empresa
    print("📦 Criando/verificando empresa...")
    company, created = Company.objects.get_or_create(
        cnpj="12.345.678/0001-90",
        defaults={
            "name": "Empresa Teste Ltda",
            "email": "contato@empresateste.com",
            "phone": "(11) 98765-4321",
            "is_active": True,
        },
    )
    if created:
        print(f"   ✅ Empresa criada: {company.name}")
    else:
        print(f"   ℹ️  Empresa já existe: {company.name}")

    # 2. Criar Customer Admin
    print("\n👤 Criando Customer Admin...")
    admin_user, created = User.objects.get_or_create(
        username="admin@empresa.com",
        defaults={
            "email": "admin@empresa.com",
            "password": make_password("senha123"),
            "first_name": "Admin",
            "last_name": "Empresa",
            "role": UserRole.CUSTOMER_ADMIN,
            "company": company,
        },
    )
    if created:
        print(f"   ✅ Admin criado: {admin_user.username}")
    else:
        print(f"   ℹ️  Admin já existe: {admin_user.username}")

    # 3. Criar 50+ Providers
    print("\n👥 Criando 50+ Providers...")
    print("   (Isso pode levar alguns segundos...)")

    num_providers = 52  # Criar 52 providers
    providers_created = 0
    providers_list = []

    for i in range(num_providers):
        provider_data = generate_provider_data()

        try:
            provider, created = Provider.objects.get_or_create(
                email=provider_data["email"],
                defaults={
                    **provider_data,
                    "company": company,
                },
            )

            if created:
                providers_created += 1
                providers_list.append(provider)
                if providers_created % 10 == 0:
                    print(f"   ✅ {providers_created} providers criados...")
        except Exception as e:
            print(f"   ⚠️  Erro ao criar provider: {e}")
            continue

    print(f"\n   📊 Total de providers criados: {providers_created}")
    print(
        f"   📊 Total de providers no sistema: {Provider.objects.filter(company=company).count()}"
    )

    # 4. Criar Payrolls para todos os meses desde 2023
    print("\n💰 Criando Payrolls desde 01/2023...")
    print("   (Isso pode levar alguns minutos...)")

    months = generate_months(2023, 1)
    total_payrolls_created = 0

    print(f"   📅 Gerando payrolls para {len(months)} meses...")

    all_providers = Provider.objects.filter(company=company)
    total_to_create = len(all_providers) * len(months)

    print(f"   📊 Total estimado: {total_to_create} payrolls")

    for month_idx, month in enumerate(months):
        month_payrolls = 0

        for provider in all_providers:
            try:
                # Verificar se já existe
                existing = Payroll.objects.filter(
                    provider=provider, reference_month=month
                ).first()

                if existing:
                    continue

                # Criar novo payroll
                payroll = create_payroll_for_provider(provider, month, company)
                month_payrolls += 1
                total_payrolls_created += 1

            except Exception as e:
                print(f"   ⚠️  Erro ao criar payroll: {e}")
                continue

        if (month_idx + 1) % 6 == 0:
            print(
                f"   ✅ Processados {month_idx + 1}/{len(months)} meses... ({total_payrolls_created} payrolls criados)"
            )

    print(f"\n   📊 Total de payrolls criados: {total_payrolls_created}")
    print(
        f"   📊 Total de payrolls no sistema: {Payroll.objects.filter(provider__company=company).count()}"
    )

    # Resumo final
    print("\n" + "=" * 70)
    print("✨ População COMPLETA concluída com sucesso!")
    print("=" * 70)
    print(f"\n📊 Resumo Final:")
    print(f"   • Empresa: {company.name}")
    print(
        f"   • Customer Admins: {User.objects.filter(company=company, role=UserRole.CUSTOMER_ADMIN).count()}"
    )
    print(f"   • Providers: {Provider.objects.filter(company=company).count()}")
    print(
        f"   • Payrolls Total: {Payroll.objects.filter(provider__company=company).count()}"
    )
    print(f"   • Período: 01/2023 - {datetime.now().strftime('%m/%Y')}")
    print(f"   • Status:")
    print(
        f"     - PAID: {Payroll.objects.filter(provider__company=company, status=PayrollStatus.PAID).count()}"
    )
    print(
        f"     - CLOSED: {Payroll.objects.filter(provider__company=company, status=PayrollStatus.CLOSED).count()}"
    )
    print(
        f"     - DRAFT: {Payroll.objects.filter(provider__company=company, status=PayrollStatus.DRAFT).count()}"
    )

    print(f"\n🔐 Credenciais de acesso:")
    print(f"   📧 Email: admin@empresa.com")
    print(f"   🔑 Senha: senha123")
    print(f"   🌐 URL: http://localhost:8000/api/auth/login/")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    populate_comprehensive_data()
