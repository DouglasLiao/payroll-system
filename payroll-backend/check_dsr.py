"""Script para verificar cálculo de DSR para janeiro/2026"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, "/app")

import django

django.setup()

from services.payroll_service import calcular_dias_mes
import calendar
from datetime import datetime
from workalendar.america import Brazil
from decimal import Decimal

# Verificar janeiro/2026
dias_uteis, domingos_feriados = calcular_dias_mes("01/2026")
print(f"Janeiro/2026:")
print(f"  Dias úteis: {dias_uteis}")
print(f"  Domingos + Feriados: {domingos_feriados}")
print(f"  Total: {dias_uteis + domingos_feriados}")

# Listar os feriados
cal = Brazil()
print(f"\nFeriados em janeiro/2026:")
for day in range(1, 32):
    date = datetime(2026, 1, day).date()
    if cal.is_holiday(date) and date.weekday() != 6:
        holiday_name = [h[1] for h in cal.get_calendar_holidays(2026) if h[0] == date]
        print(
            f'  {date.strftime("%d/%m/%Y")} - {holiday_name[0] if holiday_name else "Feriado"}'
        )

# Contar domingos
print(f"\nDomingos em janeiro/2026:")
domingos = 0
for day in range(1, 32):
    date = datetime(2026, 1, day).date()
    if date.weekday() == 6:
        domingos += 1
        print(f'  {date.strftime("%d/%m/%Y")} - Domingo')

print(f"\nTotal de domingos: {domingos}")

# Calcular DSR esperado
valor_extras = Decimal("67.73")
dsr = (valor_extras / Decimal(dias_uteis)) * Decimal(domingos_feriados)
print(f'\nDSR calculado: R$ {dsr.quantize(Decimal("0.01"))}')
print(f"  Fórmula: (R$ {valor_extras} ÷ {dias_uteis}) × {domingos_feriados}")
