"""
Serviço de Folha de Pagamento PJ

Este módulo contém a lógica de aplicação para criação e gestão de folhas
de pagamento, orquestrando os modelos Django e as funções de cálculo do domínio.
"""

from decimal import Decimal
from typing import Dict, Optional
from django.db import transaction
from django.utils import timezone
from workalendar.america import Brazil
import calendar
from datetime import datetime
from site_manage.models import Provider, Payroll, PayrollItem, PayrollStatus, ItemType


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


class PayrollService:
    """
    Serviço para gerenciamento de folhas de pagamento PJ

    Orquestra a criação, atualização e gestão do ciclo de vida das folhas,
    integrando os modelos Django com as regras de cálculo do domínio.
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
        absence_hours: Decimal = Decimal("0"),
        manual_discounts: Decimal = Decimal("0"),
        advance_already_paid: Optional[Decimal] = None,
        notes: str = None,
    ) -> Payroll:
        """
        Cria uma nova folha de pagamento para um prestador PJ.

        Args:
            provider_id: ID do prestador
            reference_month: Mês de referência (MM/YYYY)
            overtime_hours_50: Horas extras com 50% adicional
            holiday_hours: Horas trabalhadas em feriados
            night_hours: Horas com adicional noturno
            late_minutes: Minutos de atraso
            absence_hours: Horas de falta
            manual_discounts: Descontos manuais
            advance_already_paid: Adiantamento já pago (se None, calcula automaticamente)
            notes: Observações

        Returns:
            Instância de Payroll criada com todos os valores calculados

        Raises:
            Provider.DoesNotExist: Se o prestador não existir
            ValueError: Se os dados forem inválidos
        """
        # Buscar prestador
        provider = Provider.objects.get(pk=provider_id)

        # Verificar se já existe folha para este mês
        if Payroll.objects.filter(
            provider=provider, reference_month=reference_month
        ).exists():
            raise ValueError(
                f"Já existe uma folha para {provider.name} no mês {reference_month}"
            )

        # Calcular adiantamento se não foi informado
        if advance_already_paid is None:
            if provider.advance_enabled:
                advance_already_paid = (
                    provider.monthly_value
                    * provider.advance_percentage
                    / Decimal("100")
                ).quantize(Decimal("0.01"))
            else:
                advance_already_paid = Decimal("0.00")

        # Validar que adiantamento não é maior que o salário
        if advance_already_paid > provider.monthly_value:
            raise ValueError(
                f"Adiantamento (R$ {advance_already_paid}) não pode ser maior que "
                f"o valor mensal (R$ {provider.monthly_value})"
            )

        # Criar folha
        payroll = Payroll.objects.create(
            provider=provider,
            reference_month=reference_month,
            base_value=provider.monthly_value,
            advance_value=advance_already_paid,
            overtime_hours_50=overtime_hours_50,
            holiday_hours=holiday_hours,
            night_hours=night_hours,
            late_minutes=late_minutes,
            absence_hours=absence_hours,
            manual_discounts=manual_discounts,
            vt_discount=provider.vt_value,
            notes=notes,
        )

        # O método save() do modelo já calcula todos os valores
        # Agora criar os itens detalhados para transparência
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

        # Salário base após adiantamento
        items.append(
            PayrollItem(
                payroll=payroll,
                type=ItemType.CREDIT,
                description="Salário base (após adiantamento)",
                amount=payroll.remaining_value,
            )
        )

        # Horas extras 50%
        if payroll.overtime_amount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.CREDIT,
                    description=f"Horas extras 50% ({payroll.overtime_hours_50}h)",
                    amount=payroll.overtime_amount,
                )
            )

        # Feriados trabalhados
        if payroll.holiday_amount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.CREDIT,
                    description=f"Feriados trabalhados ({payroll.holiday_hours}h)",
                    amount=payroll.holiday_amount,
                )
            )

        # Adicional noturno
        if payroll.night_shift_amount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.CREDIT,
                    description=f"Adicional noturno ({payroll.night_hours}h)",
                    amount=payroll.night_shift_amount,
                )
            )

        # DSR sobre extras
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

        # Adiantamento quinzenal
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

        # Atrasos
        if payroll.late_discount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description=f"Atrasos ({payroll.late_minutes} minutos)",
                    amount=payroll.late_discount,
                )
            )

        # Faltas
        if payroll.absence_discount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description=f"Faltas ({payroll.absence_hours}h)",
                    amount=payroll.absence_discount,
                )
            )

        # Vale transporte
        if payroll.vt_discount > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description="Vale transporte",
                    amount=payroll.vt_discount,
                )
            )

        # Descontos manuais
        if payroll.manual_discounts > 0:
            items.append(
                PayrollItem(
                    payroll=payroll,
                    type=ItemType.DEBIT,
                    description="Outros descontos",
                    amount=payroll.manual_discounts,
                )
            )

        # Criar todos os itens de uma vez
        PayrollItem.objects.bulk_create(items)

    @transaction.atomic
    def close_payroll(self, payroll_id: int) -> Payroll:
        """
        Fecha a folha de pagamento, impedindo edições futuras.

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
        Marca a folha como paga.

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
    def recalculate_payroll(self, payroll_id: int, **updates) -> Payroll:
        """
        Recalcula a folha com novos valores (apenas se estiver em DRAFT).

        Args:
            payroll_id: ID da folha
            **updates: Campos a serem atualizados (ex: overtime_hours_50=10)

        Returns:
            Folha recalculada

        Raises:
            Payroll.DoesNotExist: Se a folha não existir
            ValueError: Se a folha não estiver em rascunho
        """
        payroll = Payroll.objects.select_for_update().get(pk=payroll_id)

        if payroll.status != PayrollStatus.DRAFT:
            raise ValueError(
                f"Apenas folhas em rascunho podem ser editadas. "
                f"Status atual: '{payroll.get_status_display()}'"
            )

        # Campos que podem ser atualizados
        allowed_fields = [
            "overtime_hours_50",
            "holiday_hours",
            "night_hours",
            "late_minutes",
            "absence_hours",
            "manual_discounts",
            "vt_discount",
            "notes",
        ]

        # Aplicar atualizações
        for field, value in updates.items():
            if field not in allowed_fields:
                raise ValueError(f"Campo '{field}' não pode ser atualizado")
            setattr(payroll, field, value)

        # Salvar (aciona recálculo automático)
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
            # Valores base
            "base_value": payroll.base_value,
            "hourly_rate": payroll.hourly_rate,
            "advance_value": payroll.advance_value,
            "remaining_value": payroll.remaining_value,
            # Horas
            "hours": {
                "overtime_50": payroll.overtime_hours_50,
                "holiday": payroll.holiday_hours,
                "night": payroll.night_hours,
                "late_minutes": payroll.late_minutes,
                "absence": payroll.absence_hours,
            },
            # Proventos
            "earnings": {
                "overtime": payroll.overtime_amount,
                "holiday": payroll.holiday_amount,
                "night_shift": payroll.night_shift_amount,
                "dsr": payroll.dsr_amount,
                "total": payroll.total_earnings,
            },
            # Descontos
            "discounts": {
                "late": payroll.late_discount,
                "absence": payroll.absence_discount,
                # 'dsr_on_absences': REMOVIDO - conceito CLT
                "vt": payroll.vt_discount,
                "manual": payroll.manual_discounts,
                "total": payroll.total_discounts,
            },
            # Totais
            "gross_value": payroll.gross_value,
            "net_value": payroll.net_value,
            # Itens detalhados
            "items": [
                {
                    "type": item.type,
                    "description": item.description,
                    "amount": item.amount,
                }
                for item in items
            ],
            # Metadados
            "notes": payroll.notes,
            "closed_at": payroll.closed_at,
            "paid_at": payroll.paid_at,
            "created_at": payroll.created_at,
            "updated_at": payroll.updated_at,
        }

    def reopen_payroll(self, payroll_id: int) -> Payroll:
        """
        Reabre uma folha fechada (apenas se não foi paga).

        Args:
            payroll_id: ID da folha

        Returns:
            Folha reaberta

        Raises:
            ValueError: Se a folha já foi paga
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
