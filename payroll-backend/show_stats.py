#!/usr/bin/env python
"""Script para mostrar estatísticas das folhas de pagamento."""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from site_manage.models import Payroll, Provider, PayrollStatus
from collections import Counter

print("=" * 60)
print(" RESUMO DAS FOLHAS DE PAGAMENTO CRIADAS")
print("=" * 60)
print()

# Total
total_providers = Provider.objects.count()
total_payrolls = Payroll.objects.count()

print(f"📊 Total de Prestadores: {total_providers}")
print(f"📊 Total de Folhas: {total_payrolls}")
print()

# Por status
draft = Payroll.objects.filter(status=PayrollStatus.DRAFT).count()
closed = Payroll.objects.filter(status=PayrollStatus.CLOSED).count()
paid = Payroll.objects.filter(status=PayrollStatus.PAID).count()

print("Status das Folhas:")
print(f"  - DRAFT (Rascunho):  {draft}")
print(f"  - CLOSED (Fechada):  {closed}")
print(f"  - PAID (Paga):       {paid}")
print()

# Por ano
months = Payroll.objects.values_list("reference_month", flat=True)
years = [m.split("/")[1] for m in months]
year_counts = Counter(years)

print("Folhas por Ano:")
for year in sorted(year_counts.keys()):
    print(f"  {year}: {year_counts[year]:4d} folhas")
print()

# Alguns exemplos
print("Exemplos de Folhas:")
print("-" * 60)

for payroll in Payroll.objects.select_related("provider")[:5]:
    print(f"  {payroll.provider.name} - {payroll.reference_month}")
    print(f"    Valor Líquido: R$ {payroll.net_value}")
    print(f"    Status: {payroll.get_status_display()}")
    print()

print("=" * 60)
print("✅ Dados disponíveis para:")
print("   - Exportação Excel (2.143 opções)")
print("   - Apresentações para stakeholders")
print("   - Testes de performance")
print("   - Desenvolvimento de features")
print("=" * 60)
