"""
Testes de Validação com Dados Reais

Este arquivo contém testes unitários usando valores reais fornecidos
para validar a consistência dos cálculos de folha de pagamento.
"""

import os
from decimal import Decimal

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from site_manage.models import Provider, Payroll, PayrollStatus, Company
from services.payroll_service import PayrollService


def setup_test_data():
    """Limpa dados de teste anteriores e cria empresa"""
    Payroll.objects.filter(provider__name__startswith="Funcionário Teste").delete()
    Provider.objects.filter(name__startswith="Funcionário Teste").delete()

    # Criar empresa de teste se não existir
    company, _ = Company.objects.get_or_create(
        cnpj="00000000000191",  # CNPJ de teste
        defaults={
            "name": "Empresa Teste Validação",
            "email": "teste@empresateste.com",
            "phone": "11999999999",
        },
    )

    return company


def test_case_1_real_data():
    """
    CASO 1: Dados Reais de Validação

    Dados fornecidos:
    - Salário: R$ 2.197,46
    - Horas extras: 4,52h
    - Faltas: 3 dias (assumindo 8h/dia = 24h)
    - Valor hora extra esperado: R$ 67,72
    - Valor falta esperado: R$ 219,75
    - Pagamento final esperado: R$ 1.151,88
    """
    print("\n" + "=" * 70)
    print("CASO 1: Validação com Dados Reais")
    print("=" * 70)

    company = setup_test_data()

    # Calcular carga horária (assumindo 220h padrão)
    salario = Decimal("2197.46")
    carga_horaria = 220

    # Criar provider
    provider = Provider.objects.create(
        company=company,
        name="Funcionário Teste 1",
        role="Funcionário",
        monthly_value=salario,
        monthly_hours=carga_horaria,
        advance_enabled=False,  # Sem adiantamento para simplificar
        vt_value=Decimal("0.00"),  # Sem VT para simplificar
        payment_method="PIX",
        pix_key="teste1@email.com",
    )

    print(f"\n✓ Provider criado: {provider.name}")
    print(f"  Salário mensal: R$ {provider.monthly_value}")
    print(f"  Carga horária: {provider.monthly_hours}h/mês")

    # Calcular valor/hora esperado
    valor_hora_esperado = salario / Decimal(carga_horaria)
    print(f"  Valor/hora calculado: R$ {valor_hora_esperado.quantize(Decimal('0.01'))}")

    # Dados de entrada
    horas_extras = Decimal("4.52")
    # Assumindo 3 faltas = 3 dias de 8 horas = 24 horas
    horas_falta = Decimal("24.00")

    # Criar folha
    service = PayrollService()
    payroll = service.create_payroll(
        provider_id=provider.id,
        reference_month="01/2026",
        overtime_hours_50=horas_extras,
        absence_hours=horas_falta,
        advance_already_paid=Decimal("0.00"),  # Sem adiantamento
    )

    print(f"\n✓ Folha criada: ID {payroll.id}")

    # Valores calculados pelo sistema
    print("\n📊 VALORES CALCULADOS PELO SISTEMA:")
    print(f"  Valor/hora: R$ {payroll.hourly_rate}")
    print(f"  Horas extras (4,52h): R$ {payroll.overtime_amount}")
    print(f"  Faltas (24h): R$ {payroll.absence_discount}")
    print(f"  Pagamento final: R$ {payroll.net_value}")

    # Valores esperados (fornecidos)
    print("\n📋 VALORES ESPERADOS (FORNECIDOS):")
    valor_he_esperado = Decimal("67.72")
    valor_falta_esperado = Decimal("219.75")
    pagamento_final_esperado = Decimal("1151.88")

    print(f"  Horas extras esperadas: R$ {valor_he_esperado}")
    print(f"  Faltas esperadas: R$ {valor_falta_esperado}")
    print(f"  Pagamento final esperado: R$ {pagamento_final_esperado}")

    # Comparações e tolerância de R$ 0,10 para arredondamentos
    tolerancia = Decimal("0.10")

    print("\n🔍 VERIFICAÇÃO DE CONSISTÊNCIA:")

    # Verificar hora extra
    diff_he = abs(payroll.overtime_amount - valor_he_esperado)
    if diff_he <= tolerancia:
        print(f"  ✅ Horas extras: CORRETO (diferença: R$ {diff_he})")
    else:
        print(f"  ❌ Horas extras: DIVERGENTE (diferença: R$ {diff_he})")
        print(
            f"     Calculado: R$ {payroll.overtime_amount} | Esperado: R$ {valor_he_esperado}"
        )

    # Verificar falta
    diff_falta = abs(payroll.absence_discount - valor_falta_esperado)
    if diff_falta <= tolerancia:
        print(f"  ✅ Desconto faltas: CORRETO (diferença: R$ {diff_falta})")
    else:
        print(f"  ❌ Desconto faltas: DIVERGENTE (diferença: R$ {diff_falta})")
        print(
            f"     Calculado: R$ {payroll.absence_discount} | Esperado: R$ {valor_falta_esperado}"
        )

    # Verificar pagamento final
    diff_final = abs(payroll.net_value - pagamento_final_esperado)
    if diff_final <= tolerancia:
        print(f"  ✅ Pagamento final: CORRETO (diferença: R$ {diff_final})")
        resultado_caso1 = True
    else:
        print(f"  ❌ Pagamento final: DIVERGENTE (diferença: R$ {diff_final})")
        print(
            f"     Calculado: R$ {payroll.net_value} | Esperado: R$ {pagamento_final_esperado}"
        )
        resultado_caso1 = False

    print("\n" + "=" * 70)
    if resultado_caso1 and diff_he <= tolerancia and diff_falta <= tolerancia:
        print("✅ CASO 1: TODOS OS VALORES ESTÃO CONSISTENTES!")
    else:
        print("⚠️ CASO 1: EXISTEM DIVERGÊNCIAS NOS CÁLCULOS")
    print("=" * 70)

    return resultado_caso1


def test_case_2_real_data():
    """
    CASO 2: Dados Reais de Validação

    Dados fornecidos:
    - Salário: R$ 878 (funcionário entrou dia 20/01, 12 dias trabalhados de 31)
    - Horas extras: 2h
    - Atraso: 1h50min = 110 minutos
    - Valor hora extra esperado: R$ 29,97
    - Valor atraso esperado: R$ 14,98
    - Pagamento final esperado: R$ 899,73
    """
    print("\n" + "=" * 70)
    print("CASO 2: Validação com Dados Reais - Funcionário Proporcional")
    print("=" * 70)

    company = setup_test_data()

    # Salário proporcional por 12 dias trabalhados
    salario_proporcional = Decimal("878.00")

    # Calcular carga horária proporcional
    # Se 31 dias = 220h, então 12 dias = (220/31) * 12 ≈ 85,16h
    # Mas vamos usar a proporção que faz sentido: 12 dias de 8h = 96h
    # Ou podemos calcular: (220h / 22 dias úteis) * 12 dias
    # Vou usar uma aproximação: 12 dias trabalhados de ~22 dias úteis
    # Proporção: 12/31 do mês
    carga_horaria_proporcional = int(
        (Decimal("220") * Decimal("12") / Decimal("31")).quantize(Decimal("1"))
    )

    # Criar provider com salário proporcional
    provider = Provider.objects.create(
        company=company,
        name="Funcionário Teste 2",
        role="Funcionário",
        monthly_value=salario_proporcional,
        monthly_hours=carga_horaria_proporcional,
        advance_enabled=False,  # Sem adiantamento (enunciado diz que não recebeu quinzena)
        vt_value=Decimal("0.00"),  # Sem VT para simplificar
        payment_method="PIX",
        pix_key="teste2@email.com",
    )

    print(f"\n✓ Provider criado: {provider.name}")
    print(f"  Salário proporcional (12 dias): R$ {provider.monthly_value}")
    print(f"  Carga horária proporcional: {provider.monthly_hours}h")

    # Calcular valor/hora esperado
    valor_hora_esperado = salario_proporcional / Decimal(carga_horaria_proporcional)
    print(f"  Valor/hora calculado: R$ {valor_hora_esperado.quantize(Decimal('0.01'))}")

    # Dados de entrada
    horas_extras = Decimal("2.00")
    minutos_atraso = 110  # 1h50min

    # Criar folha
    service = PayrollService()
    payroll = service.create_payroll(
        provider_id=provider.id,
        reference_month="01/2026",
        overtime_hours_50=horas_extras,
        late_minutes=minutos_atraso,
        absence_hours=Decimal("0.00"),
        advance_already_paid=Decimal("0.00"),  # Sem adiantamento
    )

    print(f"\n✓ Folha criada: ID {payroll.id}")

    # Valores calculados pelo sistema
    print("\n📊 VALORES CALCULADOS PELO SISTEMA:")
    print(f"  Valor/hora: R$ {payroll.hourly_rate}")
    print(f"  Horas extras (2h): R$ {payroll.overtime_amount}")
    print(f"  Atraso (110 min): R$ {payroll.late_discount}")
    print(f"  Pagamento final: R$ {payroll.net_value}")

    # Valores esperados (fornecidos)
    print("\n📋 VALORES ESPERADOS (FORNECIDOS):")
    valor_he_esperado = Decimal("29.97")
    valor_atraso_esperado = Decimal("14.98")
    pagamento_final_esperado = Decimal("899.73")

    print(f"  Horas extras esperadas: R$ {valor_he_esperado}")
    print(f"  Atraso esperado: R$ {valor_atraso_esperado}")
    print(f"  Pagamento final esperado: R$ {pagamento_final_esperado}")

    # Comparações e tolerância
    tolerancia = Decimal("0.10")

    print("\n🔍 VERIFICAÇÃO DE CONSISTÊNCIA:")

    # Verificar hora extra
    diff_he = abs(payroll.overtime_amount - valor_he_esperado)
    if diff_he <= tolerancia:
        print(f"  ✅ Horas extras: CORRETO (diferença: R$ {diff_he})")
    else:
        print(f"  ❌ Horas extras: DIVERGENTE (diferença: R$ {diff_he})")
        print(
            f"     Calculado: R$ {payroll.overtime_amount} | Esperado: R$ {valor_he_esperado}"
        )

    # Verificar atraso
    diff_atraso = abs(payroll.late_discount - valor_atraso_esperado)
    if diff_atraso <= tolerancia:
        print(f"  ✅ Desconto atraso: CORRETO (diferença: R$ {diff_atraso})")
    else:
        print(f"  ❌ Desconto atraso: DIVERGENTE (diferença: R$ {diff_atraso})")
        print(
            f"     Calculado: R$ {payroll.late_discount} | Esperado: R$ {valor_atraso_esperado}"
        )

    # Verificar pagamento final
    diff_final = abs(payroll.net_value - pagamento_final_esperado)
    if diff_final <= tolerancia:
        print(f"  ✅ Pagamento final: CORRETO (diferença: R$ {diff_final})")
        resultado_caso2 = True
    else:
        print(f"  ❌ Pagamento final: DIVERGENTE (diferença: R$ {diff_final})")
        print(
            f"     Calculado: R$ {payroll.net_value} | Esperado: R$ {pagamento_final_esperado}"
        )
        resultado_caso2 = False

    print("\n" + "=" * 70)
    if resultado_caso2 and diff_he <= tolerancia and diff_atraso <= tolerancia:
        print("✅ CASO 2: TODOS OS VALORES ESTÃO CONSISTENTES!")
    else:
        print("⚠️ CASO 2: EXISTEM DIVERGÊNCIAS NOS CÁLCULOS")
    print("=" * 70)

    return resultado_caso2


def run_all_validation_tests():
    """Executa todos os testes de validação"""
    print("\n" + "=" * 70)
    print("INICIANDO TESTES DE VALIDAÇÃO COM DADOS REAIS")
    print("=" * 70)

    try:
        resultado1 = test_case_1_real_data()
        resultado2 = test_case_2_real_data()

        print("\n\n" + "=" * 70)
        print("RESUMO DOS TESTES")
        print("=" * 70)
        print(
            f"Caso 1 (Funcionário com faltas): {'✅ PASSOU' if resultado1 else '❌ FALHOU'}"
        )
        print(
            f"Caso 2 (Funcionário proporcional): {'✅ PASSOU' if resultado2 else '❌ FALHOU'}"
        )
        print("=" * 70)

        if resultado1 and resultado2:
            print("✅ TODOS OS TESTES PASSARAM! Os cálculos estão consistentes.")
            return True
        else:
            print("⚠️ ALGUNS TESTES FALHARAM. Revisar lógica de cálculo.")
            return False

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERRO DURANTE EXECUÇÃO DOS TESTES: {e}")
        print("=" * 70)
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_validation_tests()
    exit(0 if success else 1)
