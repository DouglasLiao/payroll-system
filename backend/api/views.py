from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema

from .models import (
    Provider,
    Payment,
    PaymentStatus,
    Payroll,
    PayrollStatus as PayrollStatusEnum,
)
from .serializers import (
    ProviderSerializer,
    PaymentSerializer,
    PayrollSerializer,
    PayrollDetailSerializer,
    PayrollCreateSerializer,
    PayrollUpdateSerializer,
)
from .permissions import IsCustomerAdminOrReadOnly, customer_admin_only
from services.payroll_service import PayrollService

# WeasyPrint / ReportLab imports could go here
# For MVPs, we might skip complex PDF generation unless explicitly requested.
# But plan says "Download Receipt", so I'll add a placeholder that works.


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all().order_by("name")
    serializer_class = ProviderSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by("-reference", "provider__name")
    serializer_class = PaymentSerializer
    filterset_fields = ["status", "reference", "provider"]

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        payment = self.get_object()
        if payment.status == PaymentStatus.PAID:
            return Response(
                {"message": "Already paid"}, status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = PaymentStatus.PAID
        payment.paid_at = timezone.now().date()
        payment.save()
        return Response(PaymentSerializer(payment).data)


class DashboardView(APIView):
    def get(self, request):
        pending = (
            Payment.objects.filter(status=PaymentStatus.PENDING).aggregate(
                Sum("total_calculated")
            )["total_calculated__sum"]
            or 0
        )
        paid = (
            Payment.objects.filter(status=PaymentStatus.PAID).aggregate(
                Sum("total_calculated")
            )["total_calculated__sum"]
            or 0
        )

        # Recent Activity (Last 5)
        recent = PaymentSerializer(
            Payment.objects.filter(status=PaymentStatus.PAID).order_by("-paid_at")[:5],
            many=True,
        ).data

        return Response(
            {
                "stats": {"pending": pending, "paid": paid},
                "recent_activity": recent,
                # Chart data would be calculated here (aggregation by month)
            }
        )


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
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="recibo_{pk}.txt"'
        return response
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)


# ==============================================================================
# PAYROLL VIEWSET
# ==============================================================================


@extend_schema(tags=["payrolls"])
class PayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de folhas de pagamento PJ.

    Fornece operações CRUD e actions customizadas para criar, fechar e pagar folhas.
    """

    queryset = (
        Payroll.objects.all().select_related("provider").prefetch_related("items")
    )
    filterset_fields = ["status", "reference_month", "provider"]
    ordering_fields = ["reference_month", "created_at", "net_value"]
    ordering = ["-reference_month", "provider__name"]

    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na action"""
        if self.action == "retrieve":
            return PayrollDetailSerializer
        elif self.action == "calculate":
            return PayrollCreateSerializer
        elif self.action in ["update", "partial_update", "recalculate"]:
            return PayrollUpdateSerializer
        return PayrollSerializer

    @action(detail=False, methods=["post"], url_path="calculate")
    def calculate(self, request):
        """
        Cria uma nova folha de pagamento usando o PayrollService.

        POST /api/payrolls/calculate/

        Body:
        {
            "provider_id": 1,
            "reference_month": "01/2026",
            "overtime_hours_50": 10,
            "holiday_hours": 8,
            ...
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = PayrollService()

        try:
            payroll = service.create_payroll(**serializer.validated_data)
            response_serializer = PayrollDetailSerializer(payroll)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Erro ao criar folha: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """
        Fecha a folha de pagamento.

        POST /api/payrolls/{id}/close/
        """
        service = PayrollService()

        try:
            payroll = service.close_payroll(pk)
            serializer = PayrollSerializer(payroll)
            return Response(serializer.data)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        """
        Marca a folha como paga.

        POST /api/payrolls/{id}/mark-paid/
        """
        service = PayrollService()

        try:
            payroll = service.mark_as_paid(pk)
            serializer = PayrollSerializer(payroll)
            return Response(serializer.data)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["put", "patch"])
    def recalculate(self, request, pk=None):
        """
        Recalcula a folha com novos valores (apenas folhas DRAFT).

        PUT/PATCH /api/payrolls/{id}/recalculate/

        Body (todos opcionais):
        {
            "overtime_hours_50": 15,
            "notes": "Atualizado"
        }
        """
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        service = PayrollService()

        try:
            payroll = service.recalculate_payroll(pk, **serializer.validated_data)
            response_serializer = PayrollDetailSerializer(payroll)
            return Response(response_serializer.data)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        """
        Reabre uma folha fechada (apenas se não foi paga).

        POST /api/payrolls/{id}/reopen/
        """
        service = PayrollService()

        try:
            payroll = service.reopen_payroll(pk)
            serializer = PayrollSerializer(payroll)
            return Response(serializer.data)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="export-excel")
    def export_excel(self, request, pk=None):
        """
        Exporta a folha de pagamento em formato Excel (.xlsx).

        GET /api/payrolls/{id}/export-excel/

        Returns:
            Arquivo Excel formatado com todos os detalhes da folha
        """
        from services.excel_service import ExcelService
        from django.http import Http404

        try:
            payroll = self.get_object()

            # Gerar arquivo Excel
            excel_service = ExcelService()
            excel_file = excel_service.generate_payroll_excel(payroll)
            filename = excel_service.get_filename(payroll)

            # Criar resposta HTTP com arquivo
            response = HttpResponse(
                excel_file.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            return response

        except Http404:
            # Re-raise Http404 para retornar 404 corretamente
            raise
        except Exception as e:
            return Response(
                {"error": f"Erro ao gerar Excel: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """
        Sobrescreve delete para permitir apenas para folhas DRAFT.
        """
        payroll = self.get_object()

        if payroll.status != PayrollStatusEnum.DRAFT:
            return Response(
                {
                    "error": f"Apenas folhas em rascunho podem ser excluídas. Status atual: {payroll.get_status_display()}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)
