from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Provider, Payroll, PayrollStatus
from services.payroll_service import PayrollService


@receiver(post_save, sender=Provider)
def update_draft_payrolls_on_provider_change(sender, instance, **kwargs):
    """
    Quando um Prestador é atualizado (ex: salário, VT),
    recalcula todas as folhas dele que estão em RASCUNHO (DRAFT).
    """

    # Busca folhas abertas (DRAFT) deste prestador
    draft_payrolls = Payroll.objects.filter(
        provider=instance, status=PayrollStatus.DRAFT
    )

    if not draft_payrolls.exists():
        return

    service = PayrollService()

    for payroll in draft_payrolls:
        print(
            f"🔄 Recalculando folha {payroll.id} ({payroll.reference_month}) do prestador {instance.name}..."
        )
        # Recalcula usando o serviço, forçando sincronia com dados do prestador
        service.recalculate_payroll(payroll.id, sync_provider_data=True)
