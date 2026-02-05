"""
Testes para funções de cálculo de calendário e DSR dinâmico.

Valida que o cálculo de dias úteis, domingos e feriados está funcionando
corretamente usando a biblioteca workalendar para Brasil.
"""

import pytest
from decimal import Decimal
from services.payroll_service import calcular_dias_mes
from domain.payroll_calculator import calcular_dsr


class TestCalendarCalculations:
    """Testes para cálculos de calendário"""

    def test_calcular_dias_mes_janeiro_2026(self):
        """Testa cálculo de dias para janeiro/2026"""
        dias_uteis, domingos_feriados = calcular_dias_mes('2026-01')
        
        # Janeiro 2026 tem:
        # - 31 dias totais
        # - 1 feriado (Ano Novo - 01/01 é quinta)
        # - Aproximadamente 4-5 domingos
        # - Sábados não contam como dias úteis
        
        assert dias_uteis \u003e 20, "Janeiro deveria ter mais de 20 dias úteis"
        assert domingos_feriados \u003e= 5, "Janeiro deveria ter pelo menos 5 domingos + feriados"
        
        print(f"✓ Janeiro/2026: {dias_uteis} dias úteis, {domingos_feriados} domingos+feriados")

    def test_calcular_dias_mes_different_formats(self):
        """Testa se aceita diferentes formatos de data"""
        # Formato YYYY-MM
        dias1, dom1 = calcular_dias_mes('2026-01')
        
        # Formato MM/YYYY
        dias2, dom2 = calcular_dias_mes('01/2026')
        
        # Ambos devem resultar no mesmo valor
        assert dias1 == dias2, "Formatos diferentes devem resultar nos mesmos dias úteis"
        assert dom1 == dom2, "Formatos diferentes devem resultar nos mesmos domingos+feriados"
        
        print(f"✓ Ambos os formatos retornam: {dias1} dias úteis, {dom1} domingos+feriados")

    def test_calcular_dias_mes_fevereiro_2026(self):
        """Testa fevereiro 2026 (mês curto, não bissexto)"""
        dias_uteis, domingos_feriados = calcular_dias_mes('2026-02')
        
        # Fevereiro 2026 tem 28 dias (não bissexto)
        assert dias_uteis \u003e 18, "Fevereiro deveria ter mais de 18 dias úteis"
        assert dias_uteis \u003c 25, "Fevereiro com 28 dias não pode ter 25+ dias úteis"
        
        print(f"✓ Fevereiro/2026: {dias_uteis} dias úteis, {domingos_feriados} domingos+feriados")

    def test_calcular_dias_mes_dezembro_2025(self):
        """Testa dezembro 2025 (mês com múltiplos feriados)"""
        dias_uteis, domingos_feriados = calcular_dias_mes('2025-12')
        
        # Dezembro tem Natal (25)
        assert dias_uteis \u003e 20, "Dezembro deveria ter mais de 20 dias úteis"
        assert domingos_feriados \u003e= 5, "Dezembro deveria ter pelo menos 5 domingos+feriados"
        
        print(f"✓ Dezembro/2025: {dias_uteis} dias úteis, {domingos_feriados} domingos+feriados")


class TestDSRDynamicCalculation:
    """Testes para DSR dinâmico baseado em calendário"""

    def test_dsr_dynamic_calculation_basic(self):
        """Testa DSR com valores simples"""
        # (150 + 160) / 25 * 6 = 310 / 25 * 6 = 12.4 * 6 = 74.40
        resultado = calcular_dsr(
            valor_horas_extras=Decimal('150'),
            valor_feriados=Decimal('160'),
            dias_uteis=25,
            domingos_e_feriados=6
        )
        
        assert resultado == Decimal('74.40'), f"DSR deveria ser 74.40, obtido {resultado}"
        print(f"✓ DSR calculado corretamente: R$ {resultado}")

    def test_dsr_varies_by_month(self):
        """Testa que DSR varia conforme calendário do mês"""
        valor_he = Decimal('220.00')
        valor_feriado = Decimal('160.00')
        
        # Mês 1: 25 dias úteis, 6 domingos+feriados
        dsr1 = calcular_dsr(valor_he, valor_feriado, 25, 6)
        
        # Mês 2: 22 dias úteis, 8 domingos+feriados
        dsr2 = calcular_dsr(valor_he, valor_feriado, 22, 8)
        
        # DSR deve ser diferente pois a quantidade de dias varia
        assert dsr1 != dsr2, "DSR deve variar conforme calendário do mês"
        
        print(f"✓ DSR Mês 1: R$ {dsr1}")
        print(f"✓ DSR Mês 2: R$ {dsr2}")
        print(f"✓ Variação confirmada: DSR é dinâmico")

    def test_dsr_sem_extras_zero(self):
        """Testa que DSR é zero quando não há horas extras nem feriados"""
        resultado = calcular_dsr(
            valor_horas_extras=Decimal('0'),
            valor_feriados=Decimal('0'),
            dias_uteis=22,
            domingos_e_feriados=8
        )
        
        assert resultado == Decimal('0.00'), "DSR deve ser zero sem extras"
        print(f"✓ DSR sem extras: R$ {resultado}")

    def test_dsr_apenas_horas_extras(self):
        """Testa DSR apenas com horas extras (sem feriados)"""
        resultado = calcular_dsr(
            valor_horas_extras=Decimal('220.00'),
            valor_feriados=Decimal('0'),
            dias_uteis=22,
            domingos_e_feriados=8
        )
        
        # 220 / 22 * 8 = 10 * 8 = 80.00
        assert resultado == Decimal('80.00'), f"DSR deveria ser 80.00, obtido {resultado}"
        print(f"✓ DSR apenas HE: R$ {resultado}")

    def test_dsr_apenas_feriados(self):
        """Testa DSR apenas com feriados trabalhados (sem HE)"""
        resultado = calcular_dsr(
            valor_horas_extras=Decimal('0'),
            valor_feriados=Decimal('320.00'),
            dias_uteis=20,
            domingos_e_feriados=10
        )
        
        # 320 / 20 * 10 = 16 * 10 = 160.00
        assert resultado == Decimal('160.00'), f"DSR deveria ser 160.00, obtido {resultado}"
        print(f"✓ DSR apenas feriados: R$ {resultado}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
