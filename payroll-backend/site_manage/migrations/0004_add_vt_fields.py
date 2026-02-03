# Generated manually - 2026-02-03 11:10

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ("site_manage", "0003_add_proportional_salary"),
    ]

    operations = [
        # Provider Model: Replace fixed VT field with dynamic configuration
        migrations.RemoveField(
            model_name="provider",
            name="vt_value",
        ),
        migrations.AddField(
            model_name="provider",
            name="vt_enabled",
            field=models.BooleanField(
                default=False,
                verbose_name="Recebe Vale Transporte",
                help_text="Se True, VT será calculado automaticamente com base nos dias trabalhados",
            ),
        ),
        migrations.AddField(
            model_name="provider",
            name="vt_fare",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("4.60"),
                max_digits=5,
                verbose_name="Tarifa da Passagem",
                help_text="Valor da passagem de ônibus (ex: R$ 4,60 em Belém)",
            ),
        ),
        migrations.AddField(
            model_name="provider",
            name="vt_trips_per_day",
            field=models.IntegerField(
                default=4,
                verbose_name="Viagens por Dia",
                help_text="Número de viagens de ônibus por dia (ex: 2, 4, 6, etc.)",
            ),
        ),
        # Payroll Model: Add absence_days and vt_value
        migrations.AddField(
            model_name="payroll",
            name="absence_days",
            field=models.IntegerField(
                default=0,
                verbose_name="Dias de Falta",
                help_text="Número de dias de falta no mês (para cálculo de VT e desconto)",
            ),
        ),
        migrations.AddField(
            model_name="payroll",
            name="vt_value",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                editable=False,
                max_digits=10,
                verbose_name="Vale Transporte Calculado",
                help_text="Calculado automaticamente: viagens × tarifa × dias trabalhados",
            ),
        ),
        # Update help text for deprec ated fields
        migrations.AlterField(
            model_name="payroll",
            name="absence_hours",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="DEPRECATED: Use absence_days. Mantido para compatibilidade.",
                max_digits=10,
                verbose_name="Horas de Falta",
            ),
        ),
        migrations.AlterField(
            model_name="payroll",
            name="vt_discount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="DEPRECATED: Use vt_value. Mantido para compatibilidade.",
                max_digits=10,
                verbose_name="Desconto Vale Transporte",
            ),
        ),
    ]
