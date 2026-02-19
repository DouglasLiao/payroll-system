import os
import sys
from decimal import Decimal
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from domain.payroll_calculator import (
    calcular_folha_completa,
    calcular_total_descontos,
    calcular_estorno_vt,
)


def run_verification():
    print("=" * 60)
    print("🕵️  VERIFICAÇÃO DE CÁLCULO DE VT NO TOTAL DE DESCONTOS")
    print("=" * 60)

    # Cenário:
    # Salário: 2200.00
    # Faltas: 1 dia
    # VT Estorno Esperado: 4.60 * 2 * 1 = 9.20

    val_salario = Decimal("2200.00")
    dias_falta = 1

    # 1. Verificar Função de Estorno Isolada
    vt_estorno = calcular_estorno_vt(2, Decimal("4.60"), dias_falta)
    print(f"[1] Função calcular_estorno_vt(2, 4.60, 1) = {vt_estorno}")

    if vt_estorno != Decimal("9.20"):
        print("❌ ERRO NO CÁLCULO DO ESTORNO!")
        return

    # 2. Verificar Integração em calcular_folha_completa
    # Simulando o que o Service faz: calcula estorno e passa para a função

    resultado = calcular_folha_completa(
        valor_contrato_mensal=val_salario,
        absence_days=dias_falta,
        vale_transporte=vt_estorno,  # Service passa o valor calculado (9.20)
        percentual_adiantamento=Decimal("0"),
    )

    vt_no_resultado = resultado["vale_transporte"]
    total_descontos = resultado["total_descontos"]

    print(f"[2] Resultado de calcular_folha_completa:")
    print(f"    - vale_transporte: {vt_no_resultado}")
    print(f"    - desconto_falta: {resultado['desconto_falta']}")
    print(f"    - desconto_atraso: {resultado['desconto_atraso']}")
    print(f"    - descontos_manuais: {resultado['descontos_manuais']}")
    print(f"    - total_descontos: {total_descontos}")

    # Verificar soma manual
    soma_esperada = (
        resultado["desconto_falta"]
        + resultado["desconto_atraso"]
        + vt_no_resultado
        + resultado["descontos_manuais"]
    )

    print(f"[3] Validação da Soma:")
    print(f"    - Soma Esperada (Manual): {soma_esperada}")
    print(f"    - Soma Retornada (Total): {total_descontos}")

    if total_descontos == soma_esperada:
        print("✅ A soma está correta. O VT está sendo incluído.")
    else:
        print(f"❌ A soma está INCORRETA! Diferença: {total_descontos - soma_esperada}")

    if vt_no_resultado == Decimal("0.00"):
        print(
            "❌ O valor do VT no resultado é ZERO. O problema pode estar na passagem do argumento."
        )


if __name__ == "__main__":
    run_verification()
