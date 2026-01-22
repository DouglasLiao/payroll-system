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


def populate_smart_distribution():
    print("🚀 Iniciando distribuição inteligente de dados (Últimos 12 meses)...")

    company = Company.objects.first()
    if not company:
        print("❌ Nenhuma empresa encontrada. Execute populate_db.py primeiro.")
        return

    providers = list(Provider.objects.filter(company=company))
    if not providers:
        print("❌ Nenhum provider encontrado.")
        return

    print(f"📊 Processando {len(providers)} providers...")

    # Gerar últimos 12 meses + próximo mês
    months = []
    today = datetime.now()
    for i in range(12, -2, -1):  # De 12 meses atrás até mês que vem
        d = datetime(today.year, today.month, 1) - timedelta(days=i * 30)
        # Ajuste preciso de mês
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1

        months.append(f"{month:02d}/{year}")

    months = sorted(list(set(months)), key=lambda x: datetime.strptime(x, "%m/%Y"))

    for month_str in months:
        print(f"  📅 Verificando mês {month_str}...")

        month, year = map(int, month_str.split("/"))
        month_date = datetime(year, month, 1)
        is_future = month_date > datetime.now()
        is_current = (
            month_date.month == datetime.now().month
            and month_date.year == datetime.now().year
        )

        for provider in providers:
            # Verificar ou criar
            payroll, created = Payroll.objects.get_or_create(
                provider=provider,
                reference_month=month_str,
                defaults={
                    "status": PayrollStatus.DRAFT,
                    "base_value": provider.monthly_value,
                },
            )

            # Lógica de distribuição
            # Se for mês atual ou futuro: Tendência a DRAFT ou CLOSED
            # Se for passado recente (1-3 meses): CLOSED ou PAID
            # Se for passado antigo (4+ meses): PAID

            new_status = PayrollStatus.PAID

            if is_future:
                new_status = PayrollStatus.DRAFT
            elif is_current:
                new_status = random.choice(
                    [PayrollStatus.DRAFT, PayrollStatus.DRAFT, PayrollStatus.CLOSED]
                )
            else:
                months_diff = (today.year - year) * 12 + (today.month - month)

                if months_diff <= 2:
                    # 20% Draft, 40% Closed, 40% Paid
                    rand = random.random()
                    if rand < 0.2:
                        new_status = PayrollStatus.DRAFT
                    elif rand < 0.6:
                        new_status = PayrollStatus.CLOSED
                    else:
                        new_status = PayrollStatus.PAID
                elif months_diff <= 6:
                    # 10% Closed, 90% Paid
                    if random.random() < 0.1:
                        new_status = PayrollStatus.CLOSED
                    else:
                        new_status = PayrollStatus.PAID
                else:
                    new_status = PayrollStatus.PAID

            # Atualizar status se necessário (ou se acabamos de criar)
            # Também adicionar variações de valores para o gráfico não ficar plano
            if created or payroll.status != new_status or True:  # Force update
                payroll.status = new_status

                # Variação de valor (+- 10%)
                base = float(provider.monthly_value)
                variation = base * (random.uniform(-0.1, 0.1))
                # Adicionar como horas extras ou descontos para impactar o net_value
                if variation > 0:
                    payroll.overtime_hours_50 = Decimal(random.randint(1, 10))

                payroll.save()

    print("✅ Dados distribuídos com sucesso!")


if __name__ == "__main__":
    populate_smart_distribution()
