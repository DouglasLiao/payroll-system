from django.http import HttpResponse

from .models import Payment


def generate_receipt(request, pk):
    """
    Simple Text Receipt for MVP.

    Kept for legacy compatibility - generates a simple text receipt for payments.
    """
    try:
        payment = Payment.objects.get(pk=pk)
        content = f"""
        RECIBO DE PAGAMENTO
        -------------------
        Prestador: {payment.provider.name}
        Referência: {payment.reference}
        Valor: R$ {payment.total_calculated}
        Data: {payment.paid_at}
        Status: {payment.status}
        -------------------
        Gerado pelo Payroll System
        """
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="recibo_{pk}.txt"'
        return response
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)
