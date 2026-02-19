"""
Testes de integração para o PayrollService

Testa a criação, gestão e ciclo de vida completo de folhas de pagamento,
integrando modelos Django e funções de cálculo.
"""

import os
from decimal import Decimal

import sys

sys.path.append(os.getcwd())

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from site_manage.models import (
    Provider,
    Payroll,
    PayrollItem,
    PayrollStatus,
    ItemType,
    Company,
)
from services.payroll_service import PayrollService


def setup_test_data():
    """Cria dados de teste"""
    # Limpar dados existentes
    Payroll.objects.all().delete()
    Provider.objects.all().delete()
    Company.objects.all().delete()

    company = Company.objects.create(
        name="Test Company", cnpj="12345678000199", email="test@company.com"
    )

    # Criar prestador de teste
    provider = Provider.objects.create(
        name="João Silva",
        role="Desenvolvedor",
        monthly_value=Decimal("2200.00"),
        monthly_hours=220,
        advance_enabled=True,
        advance_percentage=Decimal("40.00"),
        vt_enabled=True,
        vt_fare=Decimal("4.60"),
        vt_trips_per_day=2,
        payment_method="PIX",
        pix_key="joao@email.com",
        company=company,
    )

    print(f"✓ Prestador criado: {provider.name} (ID: {provider.id})")
    return provider


def test_create_payroll():
    """Testa criação de folha de pagamento"""
    print("\n" + "=" * 70)
    print("TESTE 1: Criar Folha de Pagamento")
    print("=" * 70)

    provider = setup_test_data()
    service = PayrollService()

    # Criar folha
    payroll = service.create_payroll(
        provider_id=provider.id,
        reference_month="01/2026",
        overtime_hours_50=Decimal("10"),
        holiday_hours=Decimal("8"),
        night_hours=Decimal("20"),
        late_minutes=30,
        absence_days=1,  # Atualizado para usar dias
        manual_discounts=Decimal("0"),
        notes="Teste de integração",
    )

    print(f"\n✓ Folha criada: ID {payroll.id}")
    print(f"  Provider: {payroll.provider.name}")
    print(f"  Mês: {payroll.reference_month}")
    print(f"  Status: {payroll.get_status_display()}")

    # Verificar valores calculados
    assert payroll.hourly_rate == Decimal(
        "10.00"
    ), f"Valor/hora incorreto: {payroll.hourly_rate}"
    assert payroll.advance_value == Decimal(
        "880.00"
    ), f"Adiantamento incorreto: {payroll.advance_value}"
    assert payroll.remaining_value == Decimal(
        "1320.00"
    ), f"Saldo incorreto: {payroll.remaining_value}"
    assert payroll.overtime_amount == Decimal(
        "150.00"
    ), f"Hora extra incorreta: {payroll.overtime_amount}"
    assert payroll.holiday_amount == Decimal(
        "160.00"
    ), f"Feriado incorreto: {payroll.holiday_amount}"
    assert payroll.night_shift_amount == Decimal(
        "240.00"
    ), f"Noturno incorreto: {payroll.night_shift_amount}"

    # DSR (não mudou)
    assert payroll.dsr_amount == Decimal(
        "59.62"
    ), f"DSR incorreto: {payroll.dsr_amount}"

    # VT Estorno (Novo check)
    assert payroll.vt_value == Decimal(
        "9.20"
    ), f"VT Estorno incorreto: {payroll.vt_value}"

    assert payroll.late_discount == Decimal(
        "5.00"
    ), f"Desconto atraso incorreto: {payroll.late_discount}"
    assert payroll.absence_discount == Decimal(
        "73.33"
    ), f"Desconto falta incorreto: {payroll.absence_discount}"
    assert payroll.total_earnings == Decimal(
        "1929.62"
    ), f"Total proventos incorreto: {payroll.total_earnings}"
    assert payroll.total_discounts == Decimal(
        "87.53"
    ), f"Total descontos incorreto: {payroll.total_discounts}"
    assert payroll.net_value == Decimal(
        "1842.09"
    ), f"Valor líquido incorreto: {payroll.net_value}"

    # OBS: 1929.62 - 87.53 = 1842.09
    # O valor final depende se o adiantamento é descontado do liquido visual ou se já foi abatido?
    # No modelo, net_value = proventos - descontos.
    # Mas Adiantamento NÃO está em total_discounts.
    # Se deveria estar no calculo final:
    # Liquido = Proventos - Descontos - Adiantamento?
    # Calculadora diz: liquido = calcular_valor_liquido(proventos, total_descontos)
    # E total_descontos NÃO tem adiantamento.
    # Salvo se o adiantamento já foi descontado do "Saldo"?
    # Não, total_proventos inclui Saldo + Extras. Saldo = Base - Adiantamento.
    # Então Adiantamento já sai na origem (Saldo).
    # Logo, Net Value = Saldo + Extras - Descontos(Atraso/Falta/VT).
    # 1320 + 150 + ... = 1929.62
    # 1929.62 - 87.53 = 1842.09.
    # Correto.

    print("\n💰 Valores Calculados:")
    print(f"  Valor/hora: R$ {payroll.hourly_rate}")
    print(f"  Adiantamento: R$ {payroll.advance_value}")
    print(f"  Proventos: R$ {payroll.total_earnings}")
    print(f"  Descontos: R$ {payroll.total_discounts}")
    print(f"  Líquido: R$ {payroll.net_value}")

    # Verificar itens criados
    items = PayrollItem.objects.filter(payroll=payroll)
    assert items.count() > 0, "Nenhum item foi criado"

    credits = items.filter(type=ItemType.CREDIT).count()
    debits = items.filter(type=ItemType.DEBIT).count()

    print(f"\n📋 Itens Criados: {items.count()} total")
    print(f"  Créditos: {credits}")
    print(f"  Débitos: {debits}")

    for item in items:
        symbol = "+" if item.type == ItemType.CREDIT else "-"
        print(f"  {symbol} {item.description}: R$ {item.amount}")

    print("\n✅ TESTE 1 PASSOU!")
    return payroll


def test_close_payroll(payroll):
    """Testa fechamento de folha"""
    print("\n" + "=" * 70)
    print("TESTE 2: Fechar Folha de Pagamento")
    print("=" * 70)

    service = PayrollService()

    # Fechar folha
    closed_payroll = service.close_payroll(payroll.id)

    assert closed_payroll.status == PayrollStatus.CLOSED, "Status não mudou para CLOSED"
    assert closed_payroll.closed_at is not None, "Data de fechamento não foi definida"

    print(f"\n✓ Folha fechada: ID {closed_payroll.id}")
    print(f"  Status: {closed_payroll.get_status_display()}")
    print(f"  Fechada em: {closed_payroll.closed_at}")

    # Tentar fechar novamente (deve dar erro)
    try:
        service.close_payroll(payroll.id)
        raise AssertionError("Deveria ter dado erro ao fechar folha já fechada")
    except ValueError as e:
        print(f"\n✓ Erro esperado ao tentar fechar novamente: {e}")

    print("\n✅ TESTE 2 PASSOU!")
    return closed_payroll


def test_mark_as_paid(payroll):
    """Testa marcação como pago"""
    print("\n" + "=" * 70)
    print("TESTE 3: Marcar Folha como Paga")
    print("=" * 70)

    service = PayrollService()

    # Marcar como pago
    paid_payroll = service.mark_as_paid(payroll.id)

    assert paid_payroll.status == PayrollStatus.PAID, "Status não mudou para PAID"
    assert paid_payroll.paid_at is not None, "Data de pagamento não foi definida"

    print(f"\n✓ Folha marcada como paga: ID {paid_payroll.id}")
    print(f"  Status: {paid_payroll.get_status_display()}")
    print(f"  Paga em: {paid_payroll.paid_at}")

    print("\n✅ TESTE 3 PASSOU!")
    return paid_payroll


def test_recalculate_payroll():
    """Testa recálculo de folha"""
    print("\n" + "=" * 70)
    print("TESTE 4: Recalcular Folha de Pagamento")
    print("=" * 70)

    provider = setup_test_data()
    service = PayrollService()

    # Criar folha inicial
    payroll = service.create_payroll(
        provider_id=provider.id,
        reference_month="02/2026",
        overtime_hours_50=Decimal("5"),
        notes="Teste de recálculo",
    )

    print("\n✓ Folha inicial criada")
    print(f"  Horas extras: {payroll.overtime_hours_50}")
    print(f"  Valor horas extras: R$ {payroll.overtime_amount}")
    print(f"  Valor líquido: R$ {payroll.net_value}")

    # Recalcular com novos valores
    updated_payroll = service.recalculate_payroll(
        payroll.id,
        overtime_hours_50=Decimal("15"),
        holiday_hours=Decimal("8"),
        notes="Recalculado!",
    )

    print("\n✓ Folha recalculada")
    print(f"  Horas extras: {updated_payroll.overtime_hours_50}")
    print(f"  Valor horas extras: R$ {updated_payroll.overtime_amount}")
    print(f"  Valor líquido: R$ {updated_payroll.net_value}")
    print(f"  Observações: {updated_payroll.notes}")

    assert updated_payroll.overtime_hours_50 == Decimal(
        "15"
    ), "Horas extras não atualizadas"
    assert updated_payroll.holiday_hours == Decimal(
        "8"
    ), "Horas feriado não atualizadas"
    assert updated_payroll.notes == "Recalculado!", "Observações não atualizadas"

    # Verificar que itens foram recriados
    items_count = PayrollItem.objects.filter(payroll=updated_payroll).count()
    print(f"  Itens recriados: {items_count}")

    print("\n✅ TESTE 4 PASSOU!")


def test_get_payroll_details(payroll):
    """Testa obtenção de detalhes da folha"""
    print("\n" + "=" * 70)
    print("TESTE 5: Obter Detalhes da Folha")
    print("=" * 70)

    service = PayrollService()

    details = service.get_payroll_details(payroll.id)

    print(f"\n✓ Detalhes obtidos para folha ID {payroll.id}")
    print(f"  Provider: {details['provider']['name']}")
    print(f"  Mês: {details['reference_month']}")
    print(f"  Status: {details['status']}")
    print(f"  Valor líquido: R$ {details['net_value']}")
    print(f"  Itens: {len(details['items'])} itens")

    assert "provider" in details, "Faltando dados do provider"
    assert "earnings" in details, "Faltando dados de proventos"
    assert "discounts" in details, "Faltando dados de descontos"
    assert "items" in details, "Faltando itens"
    assert len(details["items"]) > 0, "Nenhum item retornado"

    print("\n✅ TESTE 5 PASSOU!")


def test_duplicate_payroll_error():
    """Testa erro ao criar folha duplicada"""
    print("\n" + "=" * 70)
    print("TESTE 6: Erro ao Criar Folha Duplicada")
    print("=" * 70)

    provider = setup_test_data()
    service = PayrollService()

    # Criar primeira folha
    service.create_payroll(provider_id=provider.id, reference_month="03/2026")

    print("✓ Primeira folha criada para 03/2026")

    # Tentar criar duplicada
    try:
        service.create_payroll(provider_id=provider.id, reference_month="03/2026")
        raise AssertionError("Deveria ter dado erro ao criar folha duplicada")
    except ValueError as e:
        print(f"✓ Erro esperado: {e}")

    print("\n✅ TESTE 6 PASSOU!")


def test_vt_estoppel_calculation():
    """Testa regra de estorno de VT (apenas dias de falta)"""
    print("\n" + "=" * 70)
    print("TESTE 7: Regra de Estorno de VT")
    print("=" * 70)

    # Setup Provider
    company = Company.objects.create(
        name="VT Test Co", cnpj="99999999000199", email="vt@test.com"
    )
    provider = Provider.objects.create(
        name="Maria VT",
        monthly_value=Decimal("2200.00"),
        vt_enabled=True,
        vt_fare=Decimal("4.60"),
        vt_trips_per_day=2,
        company=company,
        role="Tester",
    )

    service = PayrollService()

    # Cenário 1: Sem faltas -> VT deve ser 0 (pois é pago à parte, sem estorno)
    payroll_ok = service.create_payroll(
        provider_id=provider.id, reference_month="05/2026", absence_days=0
    )

    print(f"\n[Cenário 1] Sem faltas")
    print(f"  VT Calculado: R$ {payroll_ok.vt_value}")

    assert payroll_ok.vt_value == Decimal(
        "0.00"
    ), "VT deveria ser 0 sem faltas (pagamento separado)"

    # Cenário 2: Com 1 falta -> Estorno de 1 dia
    payroll_falta = service.create_payroll(
        provider_id=provider.id, reference_month="06/2026", absence_days=1
    )

    esperado_estorno = Decimal("4.60") * 2 * 1  # 9.20

    print(f"\n[Cenário 2] Com 1 falta")
    print(f"  VT Calculado: R$ {payroll_falta.vt_value}")
    print(f"  Total Descontos: R$ {payroll_falta.total_discounts}")

    assert (
        payroll_falta.vt_value == esperado_estorno
    ), f"VT deveria ser {esperado_estorno}"

    # Verificar se entrou no total
    # Desconto falta (1/30): 2200/30 = 73.33
    desconto_falta = (Decimal("2200") / 30).quantize(Decimal("0.01"))
    total_esperado = desconto_falta + esperado_estorno

    # Adiantamento (40%): 880.00 - NÃO entra no total_discounts
    # O sistema trata adiantamento separado do total de descontos "na folha"

    # total_esperado += adiantamento REMOVIDO

    print(f"  Desconto Falta: {desconto_falta}")
    print(f"  Soma Esperada: {total_esperado}")

    assert (
        payroll_falta.total_discounts == total_esperado
    ), f"Total descontos incorreto. Esperado {total_esperado}, obtido {payroll_falta.total_discounts}"

    print("\n✅ TESTE 7 PASSOU!")


def test_provider_updates_auto_refresh_payrolls():
    """Testa se alteração no prestador atualiza a folha em Draft automaticamente (Sinais)"""
    print("\n" + "=" * 70)
    print("TESTE 8: Atualização Automática via Sinais")
    print("=" * 70)

    # Setup
    company = Company.objects.create(
        name="Signal Test Co", cnpj="77777777000177", email="signal@test.com"
    )
    provider = Provider.objects.create(
        name="Auto Update Provider",
        monthly_value=Decimal("2000.00"),
        vt_enabled=False,
        company=company,
        role="Signal Tester",
    )

    service = PayrollService()

    # 1. Criar Folha (Draft)
    payroll = service.create_payroll(provider_id=provider.id, reference_month="11/2026")

    print(f"[1] Folha Criada. Base: {payroll.base_value}")
    assert payroll.base_value == Decimal("2000.00"), "Valor base inicial incorreto"

    # 2. Atualizar Prestador
    print(f"[2] Atualizando salário do prestador para R$ 3000.00...")
    provider.monthly_value = Decimal("3000.00")
    provider.save()  # Isso deve disparar o sinal

    # 3. Verificar Recalculo
    payroll.refresh_from_db()
    print(f"[3] Folha após update. Base: {payroll.base_value}")

    assert payroll.base_value == Decimal(
        "3000.00"
    ), f"A folha não foi atualizada! Valor ainda é {payroll.base_value}"

    print("\n✅ TESTE 8 PASSOU!")


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 70)
    print("INICIANDO TESTES DE INTEGRAÇÃO - PAYROLL SERVICE")
    print("=" * 70)

    try:
        # Teste 1: Criar folha
        payroll = test_create_payroll()

        # Teste 2: Fechar folha
        closed_payroll = test_close_payroll(payroll)

        # Teste 5: Obter detalhes (antes de marcar como pago)
        test_get_payroll_details(closed_payroll)

        # Teste 3: Marcar como pago
        test_mark_as_paid(closed_payroll)

        # Teste 4: Recalcular folha
        test_recalculate_payroll()

        # Teste 6: Erro duplicata
        test_duplicate_payroll_error()

        # Teste 7: VT Estorno
        test_vt_estoppel_calculation()

        # Teste 8: Auto Update
        test_provider_updates_auto_refresh_payrolls()

        print("\n" + "=" * 70)
        print("✅ TODOS OS 6 TESTES PASSARAM COM SUCESSO!")
        print("=" * 70)
        return True

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TESTE FALHOU: {e}")
        print("=" * 70)
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
