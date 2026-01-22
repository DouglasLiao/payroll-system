#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de teste
Cria: 1 empresa, 1 Customer Admin, e vários Providers
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from api.models import Company, User, UserRole, Provider, PaymentMethod
from django.contrib.auth.hashers import make_password


def populate_database():
    print("🚀 Iniciando população do banco de dados...")

    # 1. Criar Empresa
    print("\n📦 Criando empresa...")
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
            "is_staff": False,
            "is_superuser": False,
        },
    )
    if created:
        print(f"   ✅ Admin criado: {admin_user.username}")
        print(f"   📧 Email: admin@empresa.com")
        print(f"   🔑 Senha: senha123")
    else:
        print(f"   ℹ️  Admin já existe: {admin_user.username}")

    # 3. Criar Providers
    print("\n👥 Criando Providers...")

    providers_data = [
        {
            "name": "João Silva",
            "role": "Desenvolvedor Full Stack",
            "email": "joao.silva@email.com",
            "monthly_value": 8000.00,
            "monthly_hours": 160,
            "payment_method": PaymentMethod.PIX,
            "pix_key": "joao.silva@email.com",
        },
        {
            "name": "Maria Santos",
            "role": "Designer UX/UI",
            "email": "maria.santos@email.com",
            "monthly_value": 6500.00,
            "monthly_hours": 160,
            "payment_method": PaymentMethod.TED,
            "bank_name": "Banco do Brasil",
            "bank_agency": "1234-5",
            "bank_account": "12345-6",
        },
        {
            "name": "Pedro Costa",
            "role": "Desenvolvedor Backend",
            "email": "pedro.costa@email.com",
            "monthly_value": 7500.00,
            "monthly_hours": 160,
            "payment_method": PaymentMethod.PIX,
            "pix_key": "pedro.costa@email.com",
        },
        {
            "name": "Ana Oliveira",
            "role": "Gerente de Projetos",
            "email": "ana.oliveira@email.com",
            "monthly_value": 9000.00,
            "monthly_hours": 160,
            "payment_method": PaymentMethod.TRANSFER,
            "bank_name": "Itaú",
            "bank_agency": "5678",
            "bank_account": "98765-4",
        },
        {
            "name": "Carlos Ferreira",
            "role": "Desenvolvedor Frontend",
            "email": "carlos.ferreira@email.com",
            "monthly_value": 7000.00,
            "monthly_hours": 160,
            "payment_method": PaymentMethod.PIX,
            "pix_key": "carlos.ferreira@email.com",
        },
        {
            "name": "Juliana Lima",
            "role": "QA Engineer",
            "email": "juliana.lima@email.com",
            "monthly_value": 6000.00,
            "monthly_hours": 160,
            "payment_method": PaymentMethod.TED,
            "bank_name": "Santander",
            "bank_agency": "9012",
            "bank_account": "54321-0",
        },
        {
            "name": "Roberto Alves",
            "role": "DevOps Engineer",
            "email": "roberto.alves@email.com",
            "monthly_value": 8500.00,
            "monthly_hours": 160,
            "payment_method": PaymentMethod.PIX,
            "pix_key": "roberto.alves@email.com",
        },
        {
            "name": "Fernanda Souza",
            "role": "Product Owner",
            "email": "fernanda.souza@email.com",
            "monthly_value": 9500.00,
            "monthly_hours": 160,
            "payment_method": PaymentMethod.TRANSFER,
            "bank_name": "Bradesco",
            "bank_agency": "3456",
            "bank_account": "67890-1",
        },
    ]

    created_count = 0
    for provider_data in providers_data:
        provider, created = Provider.objects.get_or_create(
            email=provider_data["email"],
            defaults={
                **provider_data,
                "company": company,
            },
        )
        if created:
            created_count += 1
            print(f"   ✅ {provider.name} - {provider.role}")

    if created_count > 0:
        print(f"\n   📊 Total de providers criados: {created_count}")
    else:
        print(f"\n   ℹ️  Todos os providers já existem")

    # Resumo
    print("\n" + "=" * 60)
    print("✨ População concluída com sucesso!")
    print("=" * 60)
    print(f"\n📊 Resumo:")
    print(f"   • Empresa: {company.name}")
    print(
        f"   • Admins: {User.objects.filter(company=company, role=UserRole.CUSTOMER_ADMIN).count()}"
    )
    print(f"   • Providers: {Provider.objects.filter(company=company).count()}")
    print(f"\n🔐 Credenciais de acesso:")
    print(f"   📧 Email: admin@empresa.com")
    print(f"   🔑 Senha: senha123")
    print(f"   🌐 URL: http://localhost:8000/api/auth/login/")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    populate_database()
