"""
Serviço de Folha de Pagamento PJ

Este módulo contém a lógica de aplicação para criação e gestão de folhas
de pagamento, orquestrando os modelos Django e as funções de cálculo do domínio.

Seguindo o Django-Styleguide:
- Services são responsáveis por toda a lógica de negócio de escrita
- O Model.save() apenas persiste dados — sem cálculos
- Toda lógica de cálculo é centralizada aqui
"""

from decimal import Decimal
from typing import Dict, Optional
from django.db import transaction
from django.utils import timezone
from workalendar.america import Brazil
import calendar
from datetime import datetime
from site_manage.infrastructure.models import (
    Provider,
    Payroll,
    PayrollItem,
    PayrollStatus,
    ItemType,
)


def calcular_dias_mes(reference_month: str) -> tuple[int, int]:
    """
    Calcula dias úteis e domingos+feriados de um mês usando calendário brasileiro oficial.

    IMPORTANTE: Sistema exclusivo para PJ. Feriados são considerados apenas para
    cálculo do DSR contratual, não para obrigações trabalhistas CLT.

    Args:
        reference_month: Mês no formato YYYY-MM ou MM/YYYY

    Returns:
        (dias_uteis, domingos_e_feriados)

    Exemplo:
        >>> calcular_dias_mes('2026-01')
        (25, 6)  # 25 dias úteis, 6 domingos+feriados
        >>> calcular_dias_mes('01/2026')
        (25, 6)  # mesmo resultado
    """
    # Detectar formato e converter para ano e mês
    if "/" in reference_month:
        # Formato MM/YYYY
        month, year = map(int, reference_month.split("/"))
    else:
        # Formato YYYY-MM
        year, month = map(int, reference_month.split("-"))

    cal = Brazil()

    # Total de dias no mês
    _, num_days = calendar.monthrange(year, month)

    # Contar dias úteis (workalendar já considera feriados brasileiros)
    dias_uteis = 0
    domingos = 0
    feriados = 0

    for day in range(1, num_days + 1):
        date = datetime(year, month, day).date()

        # Verificar se é domingo
        if date.weekday() == 6:  # 6 = domingo
            domingos += 1
        # Verificar se é feriado (e não é domingo)
        elif cal.is_holiday(date):
            feriados += 1
        # Se não é domingo nem feriado, é dia útil
        else:
            dias_uteis += 1

    domingos_e_feriados = domingos + feriados

    return dias_uteis, domingos_e_feriados


def _calcular_valores_folha(payroll: Payroll) -> dict:
    """
    Função interna que executa todos os cálculos de uma folha.

    Centraliza a lógica que antes estava em Payroll.save().
    Retorna um dicionário com todos os campos calculados para serem
    atribuídos ao objeto Payroll antes de salvar.

    Args:
        payroll: Instância de Payroll com os dados de entrada preenchidos

    Returns:
        Dicionário com todos os campos calculados
    """
    from site_manage.domain.payroll_calculator import (
        calcular_folha_completa,
        calcular_salario_proporcional,
        calcular_vale_transporte,
        calcular_dias_trabalhados,
    )

    resultado = {}

    # ── Salário Proporcional ──────────────────────────────────────────────────
    if payroll.hired_date:
        valor_proporcional, dias_trab, _ = calcular_salario_proporcional(
            payroll.provider.monthly_value, payroll.hired_date, payroll.reference_month
        )
        resultado["proportional_base_value"] = valor_proporcional
        resultado["worked_days"] = dias_trab
        resultado["base_value"] = valor_proporcional
    else:
        resultado["worked_days"] = 0
        resultado["proportional_base_value"] = Decimal("0.00")

    base_value = resultado.get("base_value", payroll.base_value)

    # ── Vale Transporte ───────────────────────────────────────────────────────
    if payroll.provider.vt_enabled:
        dias_efetivos = calcular_dias_trabalhados(
            reference_month=payroll.reference_month,
            absence_days=payroll.absence_days,
            hired_date=payroll.hired_date,
        )
        resultado["vt_value"] = calcular_vale_transporte(
            viagens_por_dia=payroll.provider.vt_trips_per_day,
            tarifa_passagem=payroll.provider.vt_fare,
            dias_trabalhados=dias_efetivos,
        )
    else:
        resultado["vt_value"] = Decimal("0.00")

    # ── Dias Úteis / Feriados ─────────────────────────────────────────────────
    dias_uteis, domingos_feriados = calcular_dias_mes(payroll.reference_month)

    # ── Configuração da Empresa ───────────────────────────────────────────────
    calc_kwargs = {}
    try:
        config = payroll.provider.company.payroll_config
        calc_kwargs["multiplicador_extras"] = Decimal("1") + (
            config.overtime_percentage / Decimal("100")
        )
        calc_kwargs["multiplicador_feriado"] = Decimal("1") + (
            config.holiday_percentage / Decimal("100")
        )
        calc_kwargs["multiplicador_noturno"] = Decimal("1") + (
            config.night_shift_percentage / Decimal("100")
        )
    except Exception:
        # Empresa sem configuração — usa defaults do sistema
        from site_manage.infrastructure.models import PayrollMathTemplate

        default_template = PayrollMathTemplate.objects.filter(is_default=True).first()
        if not default_template:
            default_template = PayrollMathTemplate.objects.create(
                name="Padrão",
                description="Template padrão inalterável do sistema.",
                is_default=True,
                overtime_percentage=Decimal("50.00"),
                night_shift_percentage=Decimal("20.00"),
                holiday_percentage=Decimal("100.00"),
                advance_percentage=Decimal("40.00"),
            )

        calc_kwargs["multiplicador_extras"] = Decimal("1") + (
            default_template.overtime_percentage / Decimal("100")
        )
        calc_kwargs["multiplicador_feriado"] = Decimal("1") + (
            default_template.holiday_percentage / Decimal("100")
        )
        calc_kwargs["multiplicador_noturno"] = Decimal("1") + (
            default_template.night_shift_percentage / Decimal("100")
        )

    from site_manage.domain.payroll_calculator import calcular_estorno_vt

    # ── Cálculo Principal ─────────────────────────────────────────────────────
    # VT agora é calculado como ESTORNO dos dias faltados (se houver faltas)
    if payroll.absence_days > 0 and payroll.provider.vt_enabled:
        vt_para_calculo = calcular_estorno_vt(
            viagens_por_dia=payroll.provider.vt_trips_per_day,
            tarifa_passagem=payroll.provider.vt_fare,
            dias_falta=payroll.absence_days,
        )
    elif payroll.vt_discount > 0 and not payroll.provider.vt_enabled:
        # Manter compatibilidade se for um valor manual legado/fixo
        vt_para_calculo = payroll.vt_discount
    else:
        vt_para_calculo = Decimal("0.00")

    # Atualizar o objeto com o valor calculado para referência
    resultado["vt_value"] = vt_para_calculo

    advance_value = payroll.advance_value
    percentual_adiantamento = (
        (advance_value / base_value * 100) if base_value > 0 else Decimal("0")
    )

    calculated = calcular_folha_completa(
        valor_contrato_mensal=base_value,
        percentual_adiantamento=percentual_adiantamento,
        horas_extras=payroll.overtime_hours_50,
        horas_feriado=payroll.holiday_hours,
        horas_noturnas=payroll.night_hours,
        minutos_atraso=payroll.late_minutes,
        horas_falta=payroll.absence_hours,
        vale_transporte=vt_para_calculo,
        descontos_manuais=payroll.manual_discounts,
        carga_horaria_mensal=(
            payroll.provider.monthly_hours if payroll.provider_id else 220
        ),
        dias_uteis_mes=dias_uteis,
        domingos_e_feriados_mes=domingos_feriados,
        absence_days=payroll.absence_days,  # Novo parâmetro 1/30
        **calc_kwargs,
    )

    # ── Mapear resultado ──────────────────────────────────────────────────────
    resultado.update(
        {
            "hourly_rate": calculated["valor_hora"],
            "remaining_value": calculated["saldo_pos_adiantamento"],
            "overtime_amount": calculated["hora_extra_50"],
            "holiday_amount": calculated["feriado_trabalhado"],
            "night_shift_amount": calculated["adicional_noturno"],
            "dsr_amount": calculated["dsr"],
            "total_earnings": calculated["total_proventos"],
            "late_discount": calculated["desconto_atraso"],
            "absence_discount": calculated["desconto_falta"],
            "total_discounts": calculated["total_descontos"],
            "gross_value": calculated["valor_bruto"],
            "net_value": calculated["valor_liquido"],
        }
    )

    return resultado


def _apply_calculated_values(payroll: Payroll, valores: dict) -> None:
    """Aplica os valores calculados ao objeto Payroll."""
    for field, value in valores.items():
        setattr(payroll, field, value)


class PayrollService:
    """
    Serviço para gerenciamento de folhas de pagamento PJ

    Orquestra a criação, atualização e gestão do ciclo de vida das folhas,
    integrando os modelos Django com as regras de cálculo do domínio.

    Seguindo o Django-Styleguide: toda lógica de negócio vive aqui,
    não no Model.save().
    """

    @transaction.atomic
    def create_payroll(
        self,
        provider_id: int,
        reference_month: str,
        overtime_hours_50: Decimal = Decimal("0"),
        holiday_hours: Decimal = Decimal("0"),
        night_hours: Decimal = Decimal("0"),
        late_minutes: int = 0,
        absence_days: int = 0,
        absence_hours: Decimal = Decimal("0"),
        manual_discounts: Decimal = Decimal("0"),
        advance_already_paid: Optional[Decimal] = None,
        hired_date=None,
        notes: str = None,
    ) -> Payroll:
        """
        Cria uma nova folha de pagamento para um prestador PJ.

        Realiza todos os cálculos antes de persistir.

        Args:
            provider_id: ID do prestador
            reference_month: Mês de referência (MM/YYYY)
            overtime_hours_50: Horas extras com 50% adicional
            holiday_hours: Horas trabalhadas em feriados
            night_hours: Horas com adicional noturno
            late_minutes: Minutos de atraso
            absence_days: Dias de falta
            absence_hours: Horas de falta (deprecated — use absence_days)
            manual_discounts: Descontos manuais
            advance_already_paid: Adiantamento já pago (se None, calcula automaticamente)
            hired_date: Data de admissão (para salário proporcional)
            notes: Observações

        Returns:
            Instância de Payroll criada com todos os valores calculados

        Raises:
            Provider.DoesNotExist: Se o prestador não existir
            ValueError: Se os dados forem inválidos
        """
        provider = Provider.objects.select_related("company__payroll_config").get(
            pk=provider_id
        )

        # Verificar duplicata
        if Payroll.objects.filter(
            provider=provider, reference_month=reference_month
        ).exists():
            raise ValueError(
                f"Já existe uma folha para {provider.name} no mês {reference_month}"
            )

        # Calcular adiantamento
        if advance_already_paid is None:
            if provider.advance_enabled:
                advance_already_paid = (
                    provider.monthly_value
                    * provider.advance_percentage
                    / Decimal("100")
                ).quantize(Decimal("0.01"))
            else:
                advance_already_paid = Decimal("0.00")

        if advance_already_paid > provider.monthly_value:
            raise ValueError(
                f"Adiantamento (R$ {advance_already_paid}) não pode ser maior que "
                f"o valor mensal (R$ {provider.monthly_value})"
            )

        # Construir objeto sem salvar
        payroll = Payroll(
            provider=provider,
            reference_month=reference_month,
            base_value=provider.monthly_value,
            advance_value=advance_already_paid,
            overtime_hours_50=overtime_hours_50,
            holiday_hours=holiday_hours,
            night_hours=night_hours,
            late_minutes=late_minutes,
            absence_days=absence_days,
            absence_hours=absence_hours,
            manual_discounts=manual_discounts,
            vt_discount=provider.vt_fare,  # campo deprecated — mantido para compatibilidade
            hired_date=hired_date,
            notes=notes,
        )

        # Calcular todos os valores e aplicar ao objeto
        valores = _calcular_valores_folha(payroll)
        _apply_calculated_values(payroll, valores)

        # Persistir
        payroll.save()

        # Criar itens detalhados
        self._create_payroll_items(payroll)

        return payroll

    def _create_payroll_items(self, payroll: Payroll) -> None:
        """
        Cria os itens detalhados da folha para transparência.

        Args:
            payroll: Instância da folha de pagamento
        """
        items = []

        # === CRÉDITOS (PROVENTOS) ===

        items.append(
            PayrollItem(
                payroll=payroll,
                type=ItemType.CREDIT,
                description="Salário base (após adiantamento)",
                amount=payroll.remaining_value,
            )
        )

        if payroll.overtime_amount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.CREDIT,
                    description=f"Horas extras 50% ({payroll.overtime_hours_50}h)",
                    amount=payroll.overtime_amount,
                )
            )

        if payroll.holiday_amount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.CREDIT,
                    description=f"Feriados trabalhados ({payroll.holiday_hours}h)",
                    amount=payroll.holiday_amount,
                )
            )

        if payroll.night_shift_amount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.CREDIT,
                    description=f"Adicional noturno ({payroll.night_hours}h)",
                    amount=payroll.night_shift_amount,
                )
            )

        if payroll.dsr_amount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.CREDIT,
                    description="DSR sobre horas extras",
                    amount=payroll.dsr_amount,
                )
            )

        # === DÉBITOS (DESCONTOS) ===

        if payroll.advance_value > 0:
            percentage = (payroll.advance_value / payroll.base_value * 100).quantize(
                Decimal("0.01")
            )
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description=f"Adiantamento quinzenal ({percentage}%)",
                    amount=payroll.advance_value,
                )
            )

        if payroll.late_discount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description=f"Atrasos ({payroll.late_minutes} minutos)",
                    amount=payroll.late_discount,
                )
            )

        if payroll.absence_discount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description=f"Faltas ({payroll.absence_days} dias)",
                    amount=payroll.absence_discount,
                )
            )

        if payroll.vt_value > 0:
            # Descrição mais clara sobre o estorno se houver faltas
            desc_vt = "Vale transporte"
            if payroll.absence_days > 0:
                desc_vt = f"Estorno VT não utilizado ({payroll.absence_days} dias)"

            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description=desc_vt,
                    amount=payroll.vt_value,
                )
            )
        elif payroll.vt_discount > 0:
            # Compatibilidade com campo deprecated
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description="Vale transporte (manual)",
                    amount=payroll.vt_discount,
                )
            )

        if payroll.manual_discounts > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description="Outros descontos",
                    amount=payroll.manual_discounts,
                )
            )

        PayrollItem.objects.bulk_create(items)

    @transaction.atomic
    def close_payroll(self, payroll_id: int) -> Payroll:
        """
        Fecha a folha de pagamento (DRAFT → CLOSED).

        Args:
            payroll_id: ID da folha a ser fechada

        Returns:
            Folha atualizada

        Raises:
            Payroll.DoesNotExist: Se a folha não existir
            ValueError: Se a folha já estiver fechada ou paga
        """
        payroll = Payroll.objects.get(pk=payroll_id)

        if payroll.status != PayrollStatus.DRAFT:
            raise ValueError(
                f"Folha já está no status '{payroll.get_status_display()}'. "
                f"Apenas folhas em rascunho podem ser fechadas."
            )

        payroll.status = PayrollStatus.CLOSED
        payroll.closed_at = timezone.now()
        payroll.save()

        return payroll

    @transaction.atomic
    def mark_as_paid(self, payroll_id: int) -> Payroll:
        """
        Marca a folha como paga (CLOSED → PAID).

        Args:
            payroll_id: ID da folha

        Returns:
            Folha atualizada

        Raises:
            Payroll.DoesNotExist: Se a folha não existir
            ValueError: Se a folha não estiver fechada
        """
        payroll = Payroll.objects.get(pk=payroll_id)

        if payroll.status == PayrollStatus.PAID:
            raise ValueError("Folha já está marcada como paga")

        if payroll.status != PayrollStatus.CLOSED:
            raise ValueError(
                f"Folha precisa estar fechada para ser marcada como paga. "
                f"Status atual: '{payroll.get_status_display()}'"
            )

        payroll.status = PayrollStatus.PAID
        payroll.paid_at = timezone.now()
        payroll.save()

        return payroll

    @transaction.atomic
    def reopen_payroll(self, payroll_id: int) -> Payroll:
        """
        Reabre uma folha fechada (CLOSED → DRAFT).

        Args:
            payroll_id: ID da folha

        Returns:
            Folha reaberta

        Raises:
            ValueError: Se a folha já foi paga ou está em rascunho
        """
        payroll = Payroll.objects.get(pk=payroll_id)

        if payroll.status == PayrollStatus.PAID:
            raise ValueError("Folhas pagas não podem ser reabertas")

        if payroll.status == PayrollStatus.DRAFT:
            raise ValueError("Folha já está em rascunho")

        payroll.status = PayrollStatus.DRAFT
        payroll.closed_at = None
        payroll.save()

        return payroll

    @transaction.atomic
    def recalculate_payroll(
        self, payroll_id: int, sync_provider_data: bool = False, **updates
    ) -> Payroll:
        """
        Recalcula a folha com novos valores (apenas se estiver em DRAFT).

        Args:
            payroll_id: ID da folha
            sync_provider_data: Se True, atualiza dados base (salário, VT) do Prestador
            **updates: Campos a serem atualizados (ex: overtime_hours_50=10)

        Returns:
            Folha recalculada

        Raises:
            Payroll.DoesNotExist: Se a folha não existir
            ValueError: Se a folha não estiver em rascunho
        """
        payroll = (
            Payroll.objects.select_for_update()
            .select_related("provider__company")
            .get(pk=payroll_id)
        )

        if payroll.status != PayrollStatus.DRAFT:
            raise ValueError(
                f"Apenas folhas em rascunho podem ser editadas. "
                f"Status atual: '{payroll.get_status_display()}'"
            )

        allowed_fields = [
            "overtime_hours_50",
            "holiday_hours",
            "night_hours",
            "late_minutes",
            "absence_days",
            "absence_hours",
            "manual_discounts",
            "vt_discount",
            "notes",
            "provider_id",
            "hired_date",
        ]

        if sync_provider_data:
            # Atualizar dados base do prestador
            provider = payroll.provider
            payroll.base_value = provider.monthly_value

            # Recalcular adiantamento se habilitado
            if provider.advance_enabled:
                payroll.advance_value = (
                    provider.monthly_value
                    * provider.advance_percentage
                    / Decimal("100")
                ).quantize(Decimal("0.01"))
            else:
                payroll.advance_value = Decimal("0.00")

            # Atualizar defaults de VT se não estiverem travados (aqui assume-se refresh completo)
            # Mas o VT é calculado dinamicamente no _calcular_valores_folha pegando do provider.
            # O campo vt_discount é legacy, mas se for usado, atualizamos.
            payroll.vt_discount = provider.vt_fare

        for field, value in updates.items():
            if field not in allowed_fields:
                raise ValueError(f"Campo '{field}' não pode ser atualizado")

            if field == "provider_id":
                # Validar se o novo prestador já tem folha neste mês (exceto a própria)
                if (
                    Payroll.objects.filter(
                        provider_id=value, reference_month=payroll.reference_month
                    )
                    .exclude(pk=payroll.id)
                    .exists()
                ):
                    raise ValueError(
                        f"O prestador selecionado já possui uma folha para o mês {payroll.reference_month}"
                    )

                new_provider = Provider.objects.select_related(
                    "company__payroll_config"
                ).get(pk=value)

                # Validar se o novo prestador pertence à mesma empresa
                if new_provider.company_id != payroll.provider.company_id:
                    raise ValueError("O novo prestador deve pertencer à mesma empresa.")

                payroll.provider = new_provider
                payroll.base_value = new_provider.monthly_value
                if new_provider.advance_enabled:
                    payroll.advance_value = (
                        new_provider.monthly_value
                        * new_provider.advance_percentage
                        / Decimal("100")
                    ).quantize(Decimal("0.01"))
                else:
                    payroll.advance_value = Decimal("0.00")
                continue

            setattr(payroll, field, value)

        # Recalcular e aplicar
        valores = _calcular_valores_folha(payroll)
        _apply_calculated_values(payroll, valores)

        payroll.save()

        # Recriar itens
        PayrollItem.objects.filter(payroll=payroll).delete()
        self._create_payroll_items(payroll)

        return payroll

    def get_payroll_details(self, payroll_id: int) -> Dict:
        """
        Retorna detalhes completos da folha com breakdown de itens.

        Args:
            payroll_id: ID da folha

        Returns:
            Dicionário com todos os dados da folha e itens

        Raises:
            Payroll.DoesNotExist: Se a folha não existir
        """
        payroll = Payroll.objects.select_related("provider").get(pk=payroll_id)
        items = PayrollItem.objects.filter(payroll=payroll).order_by(
            "type", "description"
        )

        return {
            "id": payroll.id,
            "provider": {
                "id": payroll.provider.id,
                "name": payroll.provider.name,
                "role": payroll.provider.role,
            },
            "reference_month": payroll.reference_month,
            "status": payroll.status,
            "base_value": payroll.base_value,
            "hourly_rate": payroll.hourly_rate,
            "advance_value": payroll.advance_value,
            "remaining_value": payroll.remaining_value,
            "hours": {
                "overtime_50": payroll.overtime_hours_50,
                "holiday": payroll.holiday_hours,
                "night": payroll.night_hours,
                "late_minutes": payroll.late_minutes,
                "absence": payroll.absence_hours,
            },
            "earnings": {
                "overtime": payroll.overtime_amount,
                "holiday": payroll.holiday_amount,
                "night_shift": payroll.night_shift_amount,
                "dsr": payroll.dsr_amount,
                "total": payroll.total_earnings,
            },
            "discounts": {
                "late": payroll.late_discount,
                "absence": payroll.absence_discount,
                "vt": payroll.vt_value or payroll.vt_discount,
                "manual": payroll.manual_discounts,
                "total": payroll.total_discounts,
            },
            "gross_value": payroll.gross_value,
            "net_value": payroll.net_value,
            "items": [
                {
                    "type": item.type,
                    "description": item.description,
                    "amount": item.amount,
                }
                for item in items
            ],
            "notes": payroll.notes,
            "closed_at": payroll.closed_at,
            "paid_at": payroll.paid_at,
            "created_at": payroll.created_at,
            "updated_at": payroll.updated_at,
        }
