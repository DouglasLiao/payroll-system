"""
Testes unitários para as funções de cálculo de folha de pagamento PJ.

Estes testes validam cada função individualmente e cenários completos comparando
com os valores esperados da planilha original.
"""

from decimal import Decimal
import sys
import os

# Adicionar o diretório backend ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from domain.payroll_calculator import (
    calcular_valor_hora,
    calcular_adiantamento,
    calcular_saldo_pos_adiantamento,
    calcular_hora_extra_50,
    calcular_hora_feriado,
    calcular_adicional_noturno,
    calcular_dsr,
    calcular_total_proventos,
    calcular_desconto_atraso,
    calcular_desconto_falta,
    calcular_dsr_sobre_faltas,
    calcular_total_descontos,
    calcular_valor_liquido,
    validar_dados_entrada,
    calcular_folha_completa
)


def assert_decimal_equal(actual, expected, msg=""):
    """Helper para comparar Decimals com mensagem clara"""
    if actual != expected:
        raise AssertionError(
            f"{msg}\nEsperado: {expected}\nObtido: {actual}\nDiferença: {actual - expected}"
        )
    print(f"✓ {msg or 'Teste passou'}: {actual}")


# ==============================================================================
# TESTES - CÁLCULOS BASE
# ==============================================================================

def test_calcular_valor_hora():
    """Testa cálculo do valor da hora"""
    print("\n=== Test: Calcular Valor Hora ===")
    
    # Caso 1: Salário R$ 2.200 / 220h = R$ 10/hora
    resultado = calcular_valor_hora(Decimal('2200'), 220)
    assert_decimal_equal(resultado, Decimal('10.00'), "Salário 2200 / 220h")
    
    # Caso 2: Salário R$ 2.300 / 220h = R$ 10,45/hora
    resultado = calcular_valor_hora(Decimal('2300'), 220)
    assert_decimal_equal(resultado, Decimal('10.45'), "Salário 2300 / 220h")
    
    # Caso 3: Erro - valor zero
    try:
        calcular_valor_hora(Decimal('0'), 220)
        raise AssertionError("Deveria lançar erro para valor zero")
    except ValueError as e:
        print(f"✓ Erro esperado para valor zero: {e}")


def test_calcular_adiantamento():
    """Testa cálculo do adiantamento quinzenal"""
    print("\n=== Test: Calcular Adiantamento ===")
    
    # Caso 1: 40% de R$ 2.200 = R$ 880
    resultado = calcular_adiantamento(Decimal('2200'), Decimal('40'))
    assert_decimal_equal(resultado, Decimal('880.00'), "40% de 2200")
    
    # Caso 2: 40% de R$ 2.300 = R$ 920
    resultado = calcular_adiantamento(Decimal('2300'), Decimal('40'))
    assert_decimal_equal(resultado, Decimal('920.00'), "40% de 2300")
    
    # Caso 3: 50% de R$ 3.000 = R$ 1.500
    resultado = calcular_adiantamento(Decimal('3000'), Decimal('50'))
    assert_decimal_equal(resultado, Decimal('1500.00'), "50% de 3000")


def test_calcular_saldo_pos_adiantamento():
    """Testa cálculo do saldo após adiantamento"""
    print("\n=== Test: Calcular Saldo Pós-Adiantamento ===")
    
    # Caso 1: R$ 2.200 - R$ 880 = R$ 1.320
    resultado = calcular_saldo_pos_adiantamento(Decimal('2200'), Decimal('880'))
    assert_decimal_equal(resultado, Decimal('1320.00'), "2200 - 880")
    
    # Caso 2: R$ 2.300 - R$ 920 = R$ 1.380
    resultado = calcular_saldo_pos_adiantamento(Decimal('2300'), Decimal('920'))
    assert_decimal_equal(resultado, Decimal('1380.00'), "2300 - 920")


# ==============================================================================
# TESTES - PROVENTOS
# ==============================================================================

def test_calcular_hora_extra_50():
    """Testa cálculo de horas extras 50%"""
    print("\n=== Test: Calcular Hora Extra 50% ===")
    
    # Caso 1: 10 horas × R$ 10/h × 1.5 = R$ 150
    resultado = calcular_hora_extra_50(Decimal('10'), Decimal('10'))
    assert_decimal_equal(resultado, Decimal('150.00'), "10h extras a R$ 10/h")
    
    # Caso 2: 5 horas × R$ 10.45/h × 1.5 = R$ 78.38
    resultado = calcular_hora_extra_50(Decimal('5'), Decimal('10.45'))
    assert_decimal_equal(resultado, Decimal('78.38'), "5h extras a R$ 10.45/h")
    
    # Caso 3: Zero horas = R$ 0
    resultado = calcular_hora_extra_50(Decimal('0'), Decimal('10'))
    assert_decimal_equal(resultado, Decimal('0.00'), "0 horas extras")


def test_calcular_hora_feriado():
    """Testa cálculo de horas em feriados (100% adicional)"""
    print("\n=== Test: Calcular Hora Feriado ===")
    
    # Caso 1: 8 horas × R$ 10/h × 2 = R$ 160
    resultado = calcular_hora_feriado(Decimal('8'), Decimal('10'))
    assert_decimal_equal(resultado, Decimal('160.00'), "8h feriado a R$ 10/h")
    
    # Caso 2: 4 horas × R$ 10.45/h × 2 = R$ 83.60
    resultado = calcular_hora_feriado(Decimal('4'), Decimal('10.45'))
    assert_decimal_equal(resultado, Decimal('83.60'), "4h feriado a R$ 10.45/h")


def test_calcular_adicional_noturno():
    """Testa cálculo do adicional noturno (20%)"""
    print("\n=== Test: Calcular Adicional Noturno ===")
    
    # Caso 1: 20 horas × R$ 10/h × 0.2 = R$ 40
    resultado = calcular_adicional_noturno(Decimal('20'), Decimal('10'))
    assert_decimal_equal(resultado, Decimal('40.00'), "20h noturnas a R$ 10/h")
    
    # Caso 2: 10 horas × R$ 10.45/h × 0.2 = R$ 20.90
    resultado = calcular_adicional_noturno(Decimal('10'), Decimal('10.45'))
    assert_decimal_equal(resultado, Decimal('20.90'), "10h noturnas a R$ 10.45/h")


def test_calcular_dsr():
    """Testa cálculo do DSR sobre horas extras"""
    print("\n=== Test: Calcular DSR ===")
    
    # Caso 1: R$ 150 × 16.67% = R$ 25,00
    resultado = calcular_dsr(Decimal('150'))
    assert_decimal_equal(resultado, Decimal('25.00'), "DSR sobre R$ 150")
    
    # Caso 2: R$ 78.38 × 16.67% = R$ 13,06
    resultado = calcular_dsr(Decimal('78.38'))
    assert_decimal_equal(resultado, Decimal('13.06'), "DSR sobre R$ 78.38")


def test_calcular_total_proventos():
    """Testa cálculo do total de proventos"""
    print("\n=== Test: Calcular Total Proventos ===")
    
    # Caso completo: 1320 + 150 + 160 + 25 + 40 = 1695
    resultado = calcular_total_proventos(
        Decimal('1320'),  # saldo
        Decimal('150'),   # hora extra
        Decimal('160'),   # feriado
        Decimal('25'),    # dsr
        Decimal('40')     # noturno
    )
    assert_decimal_equal(resultado, Decimal('1695.00'), "Total de proventos")


# ==============================================================================
# TESTES - DESCONTOS
# ==============================================================================

def test_calcular_desconto_atraso():
    """Testa cálculo de desconto por atraso"""
    print("\n=== Test: Calcular Desconto Atraso ===")
    
    # Caso 1: 30 minutos = 0.5 horas × R$ 10/h = R$ 5
    resultado = calcular_desconto_atraso(30, Decimal('10'))
    assert_decimal_equal(resultado, Decimal('5.00'), "30 min de atraso a R$ 10/h")
    
    # Caso 2: 60 minutos = 1 hora × R$ 10/h = R$ 10
    resultado = calcular_desconto_atraso(60, Decimal('10'))
    assert_decimal_equal(resultado, Decimal('10.00'), "60 min de atraso a R$ 10/h")
    
    # Caso 3: 15 minutos = 0.25 horas × R$ 10/h = R$ 2.50
    resultado = calcular_desconto_atraso(15, Decimal('10'))
    assert_decimal_equal(resultado, Decimal('2.50'), "15 min de atraso a R$ 10/h")


def test_calcular_desconto_falta():
    """Testa cálculo de desconto por falta"""
    print("\n=== Test: Calcular Desconto Falta ===")
    
    # Caso 1: 8 horas × R$ 10/h = R$ 80
    resultado = calcular_desconto_falta(Decimal('8'), Decimal('10'))
    assert_decimal_equal(resultado, Decimal('80.00'), "8h de falta a R$ 10/h")
    
    # Caso 2: 4 horas × R$ 10.45/h = R$ 41.80
    resultado = calcular_desconto_falta(Decimal('4'), Decimal('10.45'))
    assert_decimal_equal(resultado, Decimal('41.80'), "4h de falta a R$ 10.45/h")


def test_calcular_dsr_sobre_faltas():
    """Testa cálculo do DSR sobre faltas"""
    print("\n=== Test: Calcular DSR sobre Faltas ===")
    
    # Caso 1: R$ 80 × 16.67% = R$ 13.33  
    resultado = calcular_dsr_sobre_faltas(Decimal('80'))
    assert_decimal_equal(resultado, Decimal('13.33'), "DSR sobre R$ 80 de faltas")
    
    # Caso 2: R$ 41.80 × 16.67% = R$ 6.97
    resultado = calcular_dsr_sobre_faltas(Decimal('41.80'))
    assert_decimal_equal(resultado, Decimal('6.97'), "DSR sobre R$ 41.80 de faltas")


def test_calcular_total_descontos():
    """Testa cálculo do total de descontos"""
    print("\n=== Test: Calcular Total Descontos ===")
    
    # Caso completo: 5 + 80 + 13.33 + 202.40 + 0 = 300.73
    resultado = calcular_total_descontos(
        Decimal('5.00'),      # atraso
        Decimal('80.00'),     # falta
        Decimal('13.33'),     # dsr sobre faltas
        Decimal('202.40'),    # VT
        Decimal('0.00')       # manuais
    )
    assert_decimal_equal(resultado, Decimal('300.73'), "Total de descontos")


# ==============================================================================
# TESTES - VALOR FINAL
# ==============================================================================

def test_calcular_valor_liquido():
    """Testa cálculo do valor líquido"""
    print("\n=== Test: Calcular Valor Líquido ===")
    
    # Caso: R$ 1.695 - R$ 300.73 = R$ 1.394,27
    resultado = calcular_valor_liquido(Decimal('1695.00'), Decimal('300.73'))
    assert_decimal_equal(resultado, Decimal('1394.27'), "Líquido: 1695 - 300.73")


# ==============================================================================
# TESTES - VALIDAÇÕES
# ==============================================================================

def test_validar_dados_entrada():
    """Testa validação de dados de entrada"""
    print("\n=== Test: Validar Dados Entrada ===")
    
    # Caso 1: Dados válidos
    dados_validos = {
        'valor_contrato_mensal': Decimal('2200'),
        'horas_extras': Decimal('10'),
        'horas_feriado': Decimal('8'),
        'horas_noturnas': Decimal('20'),
        'minutos_atraso': 30,
        'horas_falta': Decimal('8'),
        'percentual_adiantamento': 40,
        'valor_adiantamento': Decimal('880')
    }
    resultado = validar_dados_entrada(dados_validos)
    assert resultado['valido'], "Dados válidos devem passar"
    print("✓ Dados válidos aceitos")
    
    # Caso 2: Horas extras negativas
    dados_invalidos = dados_validos.copy()
    dados_invalidos['horas_extras'] = Decimal('-5')
    resultado = validar_dados_entrada(dados_invalidos)
    assert not resultado['valido'], "Horas negativas devem falhar"
    print(f"✓ Erro detectado: {resultado['erros']}")


# ==============================================================================
# TESTE - CENÁRIO COMPLETO DA PLANILHA
# ==============================================================================

def test_cenario_completo_planilha():
    """
    Testa cenário completo baseado na planilha real.
    
    Dados do exemplo:
    - Salário base: R$ 2.200,00
    - Carga horária: 220h
    - Adiantamento: 40%
    - Horas extras 50%: 10h
    - Horas feriado: 8h
    - Horas noturnas: 20h
    - Minutos de atraso: 30min
    - Horas de falta: 8h
    - Vale transporte: R$ 202,40
    """
    print("\n" + "="*70)
    print("=== TESTE CENÁRIO COMPLETO (BASEADO NA PLANILHA) ===")
    print("="*70)
    
    resultado = calcular_folha_completa(
        valor_contrato_mensal=Decimal('2200'),
        percentual_adiantamento=Decimal('40'),
        horas_extras=Decimal('10'),
        horas_feriado=Decimal('8'),
        horas_noturnas=Decimal('20'),
        minutos_atraso=30,
        horas_falta=Decimal('8'),
        vale_transporte=Decimal('202.40'),
        descontos_manuais=Decimal('0'),
        carga_horaria_mensal=220
    )
    
    print("\n📊 Resultados:")
    print(f"   Valor/hora: R$ {resultado['valor_hora']}")
    print(f"   Adiantamento: R$ {resultado['adiantamento']}")
    print(f"   Saldo pós-adiantamento: R$ {resultado['saldo_pos_adiantamento']}")
    
    print("\n💰 Proventos:")
    print(f"   Hora extra 50%: R$ {resultado['hora_extra_50']}")
    print(f"   Feriado trabalhado: R$ {resultado['feriado_trabalhado']}")
    print(f"   Adicional noturno: R$ {resultado['adicional_noturno']}")
    print(f"   DSR: R$ {resultado['dsr']}")
    print(f"   TOTAL PROVENTOS: R$ {resultado['total_proventos']}")
    
    print("\n📉 Descontos:")
    print(f"   Atrasos: R$ {resultado['desconto_atraso']}")
    print(f"   Faltas: R$ {resultado['desconto_falta']}")
    print(f"   DSR s/ faltas: R$ {resultado['dsr_sobre_faltas']}")
    print(f"   Vale transporte: R$ {resultado['vale_transporte']}")
    print(f"   Descontos manuais: R$ {resultado['descontos_manuais']}")
    print(f"   TOTAL DESCONTOS: R$ {resultado['total_descontos']}")
    
    print("\n✅ VALOR FINAL:")
    print(f"   Valor Bruto: R$ {resultado['valor_bruto']}")
    print(f"   Valor Líquido: R$ {resultado['valor_liquido']}")
    
    # Validações
    assert_decimal_equal(resultado['valor_hora'], Decimal('10.00'), "Valor/hora")
    assert_decimal_equal(resultado['adiantamento'], Decimal('880.00'), "Adiantamento")
    assert_decimal_equal(resultado['saldo_pos_adiantamento'], Decimal('1320.00'), "Saldo")
    assert_decimal_equal(resultado['hora_extra_50'], Decimal('150.00'), "Hora extra")
    assert_decimal_equal(resultado['feriado_trabalhado'], Decimal('160.00'), "Feriado")
    assert_decimal_equal(resultado['adicional_noturno'], Decimal('40.00'), "Adicional noturno")
    assert_decimal_equal(resultado['dsr'], Decimal('25.00'), "DSR")
    assert_decimal_equal(resultado['total_proventos'], Decimal('1695.00'), "Total proventos")
    assert_decimal_equal(resultado['desconto_atraso'], Decimal('5.00'), "Desconto atraso")
    assert_decimal_equal(resultado['desconto_falta'], Decimal('80.00'), "Desconto falta")
    assert_decimal_equal(resultado['dsr_sobre_faltas'], Decimal('13.33'), "DSR s/ faltas")
    assert_decimal_equal(resultado['total_descontos'], Decimal('300.73'), "Total descontos")
    assert_decimal_equal(resultado['valor_liquido'], Decimal('1394.27'), "Valor líquido")
    
    print("\n" + "="*70)
    print("✅ TODOS OS VALORES CONFEREM COM A PLANILHA!")
    print("="*70)


# ==============================================================================
# RUNNER
# ==============================================================================

def run_all_tests():
    """Executa todos os testes"""
    print("="*70)
    print("INICIANDO TESTES - FOLHA DE PAGAMENTO PJ")
    print("="*70)
    
    tests = [
        test_calcular_valor_hora,
        test_calcular_adiantamento,
        test_calcular_saldo_pos_adiantamento,
        test_calcular_hora_extra_50,
        test_calcular_hora_feriado,
        test_calcular_adicional_noturno,
        test_calcular_dsr,
        test_calcular_total_proventos,
        test_calcular_desconto_atraso,
        test_calcular_desconto_falta,
        test_calcular_dsr_sobre_faltas,
        test_calcular_total_descontos,
        test_calcular_valor_liquido,
        test_validar_dados_entrada,
        test_cenario_completo_planilha
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ FALHOU: {test.__name__}")
            print(f"   Erro: {e}")
    
    print("\n" + "="*70)
    print(f"RESULTADOS: {passed} passou(ram), {failed} falhou(ram)")
    print("="*70)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
