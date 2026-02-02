"""
Script de Teste Simples - Validação das Correções

Testa as funções corrigidas sem precisar de pytest.
"""

import os
import sys

# Adicionar o path do backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from decimal import Decimal
from domain.payroll_calculator import (
    calcular_adicional_noturno,
    calcular_desconto_falta_por_dia,
    calcular_desconto_atraso,
)


def test_adicional_noturno():
    """Teste: Adicional noturno com multiplicador 1.20"""
    print("\n" + "=" * 70)
    print("TESTE 1: Adicional Noturno (CORRIGIDO)")
    print("=" * 70)

    horas = Decimal("20.00")
    valor_hora = Decimal("10.00")
    esperado = Decimal("240.00")  # 20h × R$ 10 × 1.20

    resultado = calcular_adicional_noturno(horas, valor_hora)

    print(f"\n🌙 Entrada:")
    print(f"   Horas noturnas: {horas}h")
    print(f"   Valor/hora: R$ {valor_hora}")
    print(f"\n📊 Resultado:")
    print(f"   Esperado: R$ {esperado}")
    print(f"   Calculado: R$ {resultado}")

    if resultado == esperado:
        print(f"   ✅ PASSOU - Valor correto!")
        return True
    else:
        print(f"   ❌ FALHOU - Diferença: R$ {abs(resultado - esperado)}")
        return False


def test_desconto_falta_por_dia():
    """Teste: Desconto de falta usando salário/30"""
    print("\n" + "=" * 70)
    print("TESTE 2: Desconto de Falta por Dia (CORRIGIDO)")
    print("=" * 70)

    salario = Decimal("2200.00")
    dias_falta = 1
    esperado = Decimal("73.33")  # R$ 2200 / 30

    resultado = calcular_desconto_falta_por_dia(dias_falta, salario)

    print(f"\n❌ Entrada:")
    print(f"   Salário mensal: R$ {salario}")
    print(f"   Dias de falta: {dias_falta}")
    print(f"\n📊 Resultado:")
    print(
        f"   Valor/dia (÷ 30): R$ {(salario / Decimal('30')).quantize(Decimal('0.01'))}"
    )
    print(f"   Esperado: R$ {esperado}")
    print(f"   Calculado: R$ {resultado}")

    if resultado == esperado:
        print(f"   ✅ PASSOU - Valor correto!")
        return True
    else:
        print(f"   ❌ FALHOU - Diferença: R$ {abs(resultado - esperado)}")
        return False


def test_desconto_atraso():
    """Teste: Desconto de atraso (já estava correto)"""
    print("\n" + "=" * 70)
    print("TESTE 3: Desconto de Atraso (Verificação)")
    print("=" * 70)

    minutos = 30
    valor_hora = Decimal("10.00")
    esperado = Decimal("5.00")  # (30/60) × R$ 10

    resultado = calcular_desconto_atraso(minutos, valor_hora)

    print(f"\n⏱️ Entrada:")
    print(f"   Minutos de atraso: {minutos} min")
    print(f"   Valor/hora: R$ {valor_hora}")
    print(f"\n📊 Resultado:")
    print(f"   Esperado: R$ {esperado}")
    print(f"   Calculado: R$ {resultado}")

    if resultado == esperado:
        print(f"   ✅ PASSOU - Valor correto!")
        return True
    else:
        print(f"   ❌ FALHOU - Diferença: R$ {abs(resultado - esperado)}")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 70)
    print("VALIDAÇÃO DAS CORREÇÕES - Domain Layer")
    print("=" * 70)

    resultados = []

    # Executar testes
    resultados.append(("Adicional Noturno", test_adicional_noturno()))
    resultados.append(("Desconto Falta por Dia", test_desconto_falta_por_dia()))
    resultados.append(("Desconto Atraso", test_desconto_atraso()))

    # Resumo
    print("\n" + "=" * 70)
    print(" RESUMO DOS TESTES")
    print("=" * 70)

    passou = sum(1 for _, r in resultados if r)
    total = len(resultados)

    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  {nome}: {status}")

    print("\n" + "=" * 70)
    print(f"  Total: {passou}/{total} testes passaram")
    print("=" * 70)

    if passou == total:
        print("\n✅ SUCESSO! Todas as correções estão funcionando!")
        return 0
    else:
        print(f"\n⚠️ ATENÇÃO! {total - passou} teste(s) falharam.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
