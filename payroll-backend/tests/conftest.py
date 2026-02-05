"""
Configuração de fixtures e setup para testes com pytest.

Este arquivo é automaticamente carregado pelo pytest e contém fixtures
reutilizáveis para todos os testes.
"""

import pytest
import django
import os
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Django
django.setup()


@pytest.fixture
def sample_provider_data():
    """Dados de exemplo de um prestador PJ"""
    return {
        "name": "João Silva",
        "role": "Desenvolvedor",
        "monthly_value": "2200.00",
        "workload_hours": 220,
        "advance_percentage": 40.00,
        "advance_enabled": True,
        "vt_fare": 4.60,
        "vt_trips_per_day": 4,
        "vt_enabled": True,
    }


@pytest.fixture
def sample_payroll_data():
    """Dados de exemplo de uma folha de pagamento"""
    return {
        "reference_month": "01/2026",
        "overtime_hours_50": 10,
        "holiday_hours": 8,
        "night_hours": 20,
        "late_minutes": 30,
        "absence_hours": 8,
        "manual_discounts": 0,
    }


@pytest.fixture
def calendar_january_2026():
    """Informações de calendário para Janeiro/2026"""
    return {"dias_uteis": 25, "domingos_feriados": 6, "reference_month": "01/2026"}


@pytest.fixture
def expected_calculations_full_scenario():
    """Valores esperados para o cenário completo do modelo de negócio"""
    from decimal import Decimal

    return {
        "valor_hora": Decimal("10.00"),
        "adiantamento": Decimal("880.00"),
        "saldo": Decimal("1320.00"),
        "hora_extra_50": Decimal("150.00"),
        "feriado_trabalhado": Decimal("160.00"),
        "adicional_noturno": Decimal("240.00"),
        "dsr": Decimal("74.40"),  # (150+160)/25*6
        "total_proventos": Decimal("1944.40"),
        "desconto_atraso": Decimal("5.00"),
        "desconto_falta": Decimal("80.00"),
        "total_descontos": Decimal("287.40"),  # Sem VT para este cenário
        "valor_liquido": Decimal("1657.00"),
    }
