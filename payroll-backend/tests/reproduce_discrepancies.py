import os
import sys
from decimal import Decimal
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from domain.payroll_calculator import calcular_folha_completa


def run_reproduction():
    print("=" * 60)
    print("🕵️  REPRODUÇÃO DE DISCREPÂNCIAS DE FOLHA DE PAGAMENTO")
    print("=" * 60)

    # Cenário do Documento (Janeiro/2026)
    # Salário: 2.200,00
    # Faltas: 1 dia (8 horas)
    # VT: R$ 4,60 * 2 = 9,20 por dia. 25 dias úteis.

    # ---------------------------------------------------------
    # 1. TESTE DE FALTAS (1/30 Rule)
    # ---------------------------------------------------------
    print("\n[1] ANÁLISE DE FALTAS")

    # Simulação Atual (passando horas)
    resultado = calcular_folha_completa(
        valor_contrato_mensal=Decimal("2200.00"),
        absence_days=1,  # Novo parâmetro da Regra 1/30
        horas_falta=Decimal("8"),
        # Configuração para isolar o teste
        percentual_adiantamento=Decimal("0"),
        dias_uteis_mes=25,
        domingos_e_feriados_mes=6,
    )

    desconto_falta_atual = resultado["desconto_falta"]

    # Regra Documentada: 2200 / 30 * 1 = 73.33
    esperado_doc = Decimal("2200") / Decimal("30")
    esperado_doc = esperado_doc.quantize(Decimal("0.01"))

    print(f"   Cenário: 1 Dia de Falta (8h)")
    print(f"   Valor Atual (Cálculo por Horas): R$ {desconto_falta_atual}")
    print(f"   Valor Esperado (Regra 1/30):     R$ {esperado_doc}")

    if desconto_falta_atual != esperado_doc:
        print(
            f"   ❌ DISCREPÂNCIA CONFIRMADA! Valor Atual: {desconto_falta_atual} != Esperado: {esperado_doc}"
        )
    else:
        print("   ✅ COMPORTAMENTO CORRETO: Faltas calculadas como 1/30.")

    # ---------------------------------------------------------
    # 2. TESTE DE VALE TRANSPORTE (Estorno vs Desconto Cheio)
    # ---------------------------------------------------------
    print("\n[2] ANÁLISE DE VALE TRANSPORTE")

    # Configurar VT
    vt_diario = Decimal("4.60") * 2  # 9.20
    dias_uteis = 25
    dias_falta = 1
    dias_trabalhados = dias_uteis - dias_falta  # 24

    # Simular calculo via Domain (agora que o domain absorve parte da logica se absence_days for passado)
    # Precisamos passar absence_days para ativar o calculo de estorno
    resultado_vt = calcular_folha_completa(
        valor_contrato_mensal=Decimal("2200.00"),
        absence_days=1,  # Ativa Estorno
        vale_transporte=Decimal(
            "9.20"
        ),  # Simulando o que o Service vai passar (Estorno calculado)
        percentual_adiantamento=Decimal("0"),
    )

    desconto_vt_atual = resultado_vt["vale_transporte"]

    # Regra Documentada: Descontar apenas o VT do dia faltado
    vt_esperado_doc = vt_diario * dias_falta  # 9.20

    print(f"   Cenário: 25 dias úteis, 1 falta")
    print(f"   Valor Atual (Custo do que trabalhou): R$ {desconto_vt_atual}")
    print(f"   Valor Esperado (Estorno do que faltou): R$ {vt_esperado_doc}")

    if desconto_vt_atual > vt_esperado_doc:
        print(
            "   ❌ DISCREPÂNCIA CONFIRMADA! O sistema está descontando o VT dos dias trabalhados (R$ 220,80) em vez de estornar o dia não trabalhado (R$ 9,20)."
        )
    else:
        print("   ✅ COMPORTAMENTO CORRETO.")

    # OBS: O teste unitário do Domain (este script) testa o `calcular_folha_completa`.
    # O `calcular_folha_completa` apenas SOMA o que recebe de `vale_transporte` nos descontos.
    # Quem calcula o valor é o Service ou quem chama.
    # Então para validar se o SISTEMA está certo, este script deveria testar:
    # 1. Se `calcular_estorno_vt` devolve o valor certo.
    # 2. Se `calcular_folha_completa` integra isso certo.

    from domain.payroll_calculator import calcular_estorno_vt

    vt_estorno_calc = calcular_estorno_vt(2, Decimal("4.60"), 1)

    if vt_estorno_calc == vt_esperado_doc:
        print(
            f"   ✅ COMPORTAMENTO CORRETO: Função calcular_estorno_vt retornou R$ {vt_estorno_calc}"
        )
    else:
        print(f"   ❌ ERRO: calcular_estorno_vt retornou {vt_estorno_calc}")


if __name__ == "__main__":
    run_reproduction()
