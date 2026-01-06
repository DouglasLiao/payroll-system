from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse
from .models import Provider, Payment, PaymentStatus
from .serializers import ProviderSerializer, PaymentSerializer

# WeasyPrint / ReportLab imports could go here
# For MVPs, we might skip complex PDF generation unless explicitly requested.
# But plan says "Download Receipt", so I'll add a placeholder that works.

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all().order_by('name')
    serializer_class = ProviderSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('-reference', 'provider__name')
    serializer_class = PaymentSerializer
    filterset_fields = ['status', 'reference', 'provider']

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        payment = self.get_object()
        if payment.status == PaymentStatus.PAID:
            return Response({'message': 'Already paid'}, status=status.HTTP_400_BAD_REQUEST)
        
        payment.status = PaymentStatus.PAID
        payment.paid_at = timezone.now().date()
        payment.save()
        return Response(PaymentSerializer(payment).data)

class DashboardView(APIView):
    def get(self, request):
        pending = Payment.objects.filter(status=PaymentStatus.PENDING).aggregate(Sum('total_calculated'))['total_calculated__sum'] or 0
        paid = Payment.objects.filter(status=PaymentStatus.PAID).aggregate(Sum('total_calculated'))['total_calculated__sum'] or 0
        
        # Recent Activity (Last 5)
        recent = PaymentSerializer(
            Payment.objects.filter(status=PaymentStatus.PAID).order_by('-paid_at')[:5], 
            many=True
        ).data

        return Response({
            'stats': {
                'pending': pending,
                'paid': paid
            },
            'recent_activity': recent,
            # Chart data would be calculated here (aggregation by month)
        })

def generate_receipt(request, pk):
    # Simple Text Receipt for MVP
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
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="recibo_{pk}.txt"'
        return response
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)
