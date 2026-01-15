#!/usr/bin/env python
"""
Script de teste para verificar o cálculo correto do DSR
"""
import sys
import os
from decimal import Decimal

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from domain.payroll_calculator import calcular_dsr, calcular_folha_completa
from services.payroll_service import calcular_dias_mes

def test_calcular_dias_mes():
    """Testa cálculo de dias úteis e feriados"""
    print("\n=== Teste: calcular_dias_mes ===")
    
    # Janeiro 2026
    dias_uteis, domingos_feriados = calcular_dias_mes('2026-01')
    print(f"Janeiro/2026: {dias_uteis} dias úteis, {domingos_feriados} domingos+feriados")
    assert dias_uteis > 0, "Dias úteis deve ser maior que zero"
    assert domingos_feriados > 0, "Domingos e feriados deve ser maior que zero"
    print("✅ Teste passou!")

def test_calcular_dsr():
    """Testa novo cálculo do DSR"""
    print("\n=== Teste: calcular_dsr ===")
    
    # Exemplo do usuário
    valor_he = Decimal('220.00')
    valor_feriado = Decimal('160.00')
    dias_uteis = 25
    domingos_feriados = 6
    
    dsr = calcular_dsr(valor_he, valor_feriado, dias_uteis, domingos_feriados)
    
    # (220 + 160) / 25 * 6 = 91.20
    esperado = Decimal('91.20')
    
    print(f"Horas Extras: R$ {valor_he}")
    print(f"Feriados: R$ {valor_feriado}")
    print(f"Dias Úteis: {dias_uteis}")
    print(f"Domingos+Feriados: {domingos_feriados}")
    print(f"DSR Calculado: R$ {dsr}")
    print(f"DSR Esperado: R$ {esperado}")
    
    assert dsr == esperado, f"DSR deveria ser {esperado}, mas foi {dsr}"
    print("✅ Teste passou!")

def test_calcular_dsr_sem_extras():
    """Testa DSR quando não há extras"""
    print("\n=== Teste: calcular_dsr sem extras ===")
    
    dsr = calcular_dsr(Decimal('0'), Decimal('0'), 22, 8)
    
    print(f"DSR sem extras: R$ {dsr}")
    assert dsr == Decimal('0.00'), "DSR deveria ser zero quando não há extras"
    print("✅ Teste passou!")

def test_folha_completa():
    """Testa cálculo completo da folha"""
    print("\n=== Teste: calcular_folha_completa ===")
    
    resultado = calcular_folha_completa(
        valor_contrato_mensal=Decimal('2200.00'),
        percentual_adiantamento=Decimal('40.00'),
        horas_extras=Decimal('10'),
        horas_feriado=Decimal('8'),
        horas_noturnas=Decimal('20'),
        minutos_atraso=30,
        horas_falta=Decimal('8'),
        vale_transporte=Decimal('202.40'),
        descontos_manuais=Decimal('0'),
        carga_horaria_mensal=220,
        dias_uteis_mes=25,
        domingos_e_feriados_mes=6
    )
    
    print(f"Valor Hora: R$ {resultado['valor_hora']}")
    print(f"Horas Extras: R$ {resultado['hora_extra_50']}")
    print(f"Feriados: R$ {resultado['feriado_trabalhado']}")
    print(f"DSR: R$ {resultado['dsr']}")
    print(f"Total Proventos: R$ {resultado['total_proventos']}")
    print(f"Total Descontos: R$ {resultado['total_descontos']}")
    print(f"Valor Líquido: R$ {resultado['valor_liquido']}")
    
    # Verificar que dsr_sobre_faltas não existe mais
    assert 'dsr_sobre_faltas' not in resultado, "dsr_sobre_faltas não deveria existir"
    
    # Verificar DSR correto
    # (150 + 160) / 25 * 6 = 74.40
    assert resultado['dsr'] == Decimal('74.40'), f"DSR deveria ser 74.40, mas foi {resultado['dsr']}"
    
    print("✅ Teste passou!")

if __name__ == '__main__':
    print("=" * 60)
    print("TESTES DE CORREÇÃO DO DSR - Sistema PJ-only")
    print("=" * 60)
    
    try:
        test_calcular_dias_mes()
        test_calcular_dsr()
        test_calcular_dsr_sem_extras()
        test_folha_completa()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
