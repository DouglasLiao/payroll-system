from decimal import Decimal
import sys
import os
import unittest

# Adicionar o diretório backend ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from domain.payroll_calculator import (
    calcular_hora_extra_50,
    calcular_hora_feriado,
    calcular_adicional_noturno,
    calcular_folha_completa,
    DEFAULT_MULT_HORA_EXTRA,
    DEFAULT_MULT_FERIADO,
    DEFAULT_MULT_NOTURNO,
)


class TestPayrollCalculatorDynamic(unittest.TestCase):

    def test_backward_compatibility(self):
        """Testa se os defaults mantêm o comportamento original"""
        valor_hora = Decimal("10.00")

        # Hora Extra (Default 1.5)
        he_val = calcular_hora_extra_50(Decimal("10"), valor_hora)
        self.assertEqual(he_val, Decimal("150.00"))  # 10 * 10 * 1.5

        # Feriado (Default 2.0)
        fer_val = calcular_hora_feriado(Decimal("10"), valor_hora)
        self.assertEqual(fer_val, Decimal("200.00"))  # 10 * 10 * 2.0

        # Noturno (Default 1.2)
        not_val = calcular_adicional_noturno(Decimal("10"), valor_hora)
        self.assertEqual(not_val, Decimal("120.00"))  # 10 * 10 * 1.2

    def test_dynamic_multipliers(self):
        """Testa multiplicadores customizados"""
        valor_hora = Decimal("10.00")

        # Hora Extra 100% (Multiplicador 2.0)
        he_val = calcular_hora_extra_50(
            Decimal("10"), valor_hora, multiplicador=Decimal("2.0")
        )
        self.assertEqual(he_val, Decimal("200.00"))  # 10 * 10 * 2.0

        # Feriado 150% (Multiplicador 2.5) -> Feriado geralmente é 100% (2x), mas testando custom
        fer_val = calcular_hora_feriado(
            Decimal("10"), valor_hora, multiplicador=Decimal("2.5")
        )
        self.assertEqual(fer_val, Decimal("250.00"))  # 10 * 10 * 2.5

        # Noturno 30% (Multiplicador 1.3)
        not_val = calcular_adicional_noturno(
            Decimal("10"), valor_hora, multiplicador=Decimal("1.3")
        )
        self.assertEqual(not_val, Decimal("130.00"))  # 10 * 10 * 1.3

    def test_folha_completa_dynamic(self):
        """Testa o cálculo da folha completa com configurações customizadas"""

        # Cenário: Empresa paga 100% de hora extra (2.0) e 50% noturno (1.5)
        resultado = calcular_folha_completa(
            valor_contrato_mensal=Decimal("2200"),  # Hora = 10.00
            horas_extras=Decimal("10"),
            horas_noturnas=Decimal("10"),
            multiplicador_extras=Decimal("2.0"),
            multiplicador_noturno=Decimal("1.5"),
        )

        # Hora Extra: 10h * R$10 * 2.0 = R$ 200.00
        self.assertEqual(resultado["hora_extra_50"], Decimal("200.00"))

        # Noturno: 10h * R$10 * 1.5 = R$ 150.00
        self.assertEqual(resultado["adicional_noturno"], Decimal("150.00"))


if __name__ == "__main__":
    unittest.main()
