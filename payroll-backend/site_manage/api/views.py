"""
site_manage/views.py — Payroll domain views.

Auth, registration, company, subscription, and config views have moved to users/views.py.

ViewSets:
  - ProviderViewSet       → /providers/
  - PayrollViewSet        → /payrolls/
  - DashboardView         → /dashboard/
  - generate_receipt      → /receipt/<pk>/
"""

from datetime import datetime, timedelta

from django.http import HttpResponse
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from site_manage.api.serializers import (
    PayrollCreateSerializer,
    PayrollDetailSerializer,
    PayrollSerializer,
    PayrollUpdateSerializer,
    ProviderSerializer,
)
from site_manage.pagination import CustomPageNumberPagination
from site_manage.application.commands.email_service import EmailService
from site_manage.application.commands.payroll_service import PayrollService
from site_manage.application.queries.selectors import (
    dashboard_stats_for_company,
    payroll_list_for_user,
    provider_list_for_user,
)
from site_manage.infrastructure.models import Payment, Payroll, Provider
from site_manage.permissions import IsCustomerAdminOrReadOnly
from users.application.queries.selectors import subscription_can_add_provider
from users.models import User, UserRole

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

# ==============================================================================
# PROVIDERS
# ==============================================================================


class ProviderListCreateAPIView(APIView):
    """
    Lista Providers do tenant ou cria novo.

    GET /providers/
    POST /providers/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        # Seleciona de acordo com tenant/user rules
        providers = provider_list_for_user(user=request.user).order_by("name")

        # Filtros manuais básicos compatíveis com DjangoFilterBackend legados
        role_filter = request.query_params.get("role")
        if role_filter:
            providers = providers.filter(role=role_filter)

        payment_method_filter = request.query_params.get("payment_method")
        if payment_method_filter:
            providers = providers.filter(payment_method=payment_method_filter)

        search_query = request.query_params.get("search")
        if search_query:
            providers = providers.filter(
                Q(name__icontains=search_query) | Q(role__icontains=search_query)
            )

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(providers, request, view=self)
        if paginated_queryset is not None:
            serializer = ProviderSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"email": ["E-mail é obrigatório para envio do convite aos colaboradores."]}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure no user already exists with this email
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            return Response({"email": ["E-mail já cadastrado no sistema."]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProviderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Associa à empresa do Admin
        company = None
        if request.user.role == "CUSTOMER_ADMIN":
            company = request.user.company
            if not subscription_can_add_provider(company=company):
                return Response(
                    {
                        "detail": "Limite de prestadores atingido. Faça o upgrade do seu plano para complementar."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            provider = serializer.save(company=company)
        else:
            provider = serializer.save()

        company_to_use = company if company else provider.company
        
        # Gerar usuário inativo para o prestador acessá-lo via convite (Onboarding)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=None,
            role=UserRole.PROVIDER,
            company=company_to_use,
            is_active=False
        )
        provider.user = user
        provider.save()

        # Gerar link de convite assinado
        token_generator = PasswordResetTokenGenerator()
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        invite_url = f"{frontend_url}/invite/{uidb64}/{token}"

        # Enviar e-mail de convite
        try:
            send_mail(
                subject=f"Convite ao portal - {company_to_use.name}",
                message=f"Olá,\n\nVocê foi convidado pela empresa {company_to_use.name} para o sistema de pagamentos de parceiros.\n\nAcesse o link abaixo para concluir seu cadastro:\n\n{invite_url}\n\nAbraços,\nEquipe Payroll System.",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@payrollsystem.com'),
                recipient_list=[email],
                fail_silently=True,  # No ambiente local MailHog intercepta, mas em prod se falhar evitamos 500
            )
        except Exception as e:
            # Em um cenário real, poderíamos enfileirar via Celery
            print(f"Erro ao enviar email de convite: {e}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AcceptInviteAPIView(APIView):
    """
    Finaliza o onboarding do Colaborador: Ativa a conta, define a senha e preenche os dados finais.
    GET /accept-invite/ ?uidb64=...&token=... - Retorna dados do Provider para pré-preenchimento
    POST /accept-invite/  - Salva senha e ativa conta
    """
    permission_classes = []  # Público para quem tem o link

    def _get_user_and_provider(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None, None, 'Link inválido ou expirado.'

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return None, None, 'Link de convite inválido ou expirado. Solicite novo reenvio.'

        provider = getattr(user, 'provider_profile', None)
        return user, provider, None

    def get(self, request, *args, **kwargs):
        uidb64 = request.query_params.get('uidb64')
        token = request.query_params.get('token')

        if not uidb64 or not token:
            return Response({'error': 'Parâmetros inválidos.'}, status=status.HTTP_400_BAD_REQUEST)

        user, provider, error = self._get_user_and_provider(uidb64, token)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'email': user.email,
            'name': provider.name if provider else '',
            'role': provider.role if provider else '',
            'company': user.company.name if user.company else '',
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        password = request.data.get("password")
        name = request.data.get("name")
        address = request.data.get("address")
        pix_key = request.data.get("pix_key")

        if not all([uidb64, token, password]):
            return Response({"error": "Senha é obrigatória."}, status=status.HTTP_400_BAD_REQUEST)

        user, provider, error = self._get_user_and_provider(uidb64, token)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        # Ativar o Usuário
        user.set_password(password)
        user.is_active = True
        if name:
            user.first_name = name.split(" ")[0]
            if " " in name:
                user.last_name = name.split(" ", 1)[1]
        user.save()

        # Atualizar o Prestador
        if provider:
            if name:
                provider.name = name
            if address:
                provider.address = address
            if pix_key:
                provider.pix_key = pix_key
            provider.save()

        return Response({"message": "Convite aceito com sucesso! Redirecionando..."}, status=status.HTTP_200_OK)


class ProviderDetailAPIView(APIView):
    """
    Consulta, Atualiza ou Exclui um Provider específico.

    GET /providers/{id}/
    PUT /providers/{id}/
    PATCH /providers/{id}/
    DELETE /providers/{id}/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get_object(self, request, pk):
        try:
            # Garante tenant isolation
            provider = provider_list_for_user(user=request.user).get(pk=pk)
            return provider
        except Provider.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        provider = self.get_object(request, pk)
        if not provider:
            return Response(
                {"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProviderSerializer(provider)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        provider = self.get_object(request, pk)
        if not provider:
            return Response(
                {"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProviderSerializer(provider, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        provider = self.get_object(request, pk)
        if not provider:
            return Response(
                {"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProviderSerializer(provider, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        provider = self.get_object(request, pk)
        if not provider:
            return Response(
                {"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        provider.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# PAYROLLS
# ==============================================================================


class PayrollListAPIView(APIView):
    """
    Lista de Payrolls do tenant.
    GET /payrolls/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        payrolls = payroll_list_for_user(user=request.user).order_by(
            "-reference_month", "provider__name"
        )

        # Filtros manuais básicos compensando DjangoFilterBackend
        status_filter = request.query_params.get("status")
        if status_filter:
            payrolls = payrolls.filter(status=status_filter)

        ref_month_filter = request.query_params.get("reference_month")
        if ref_month_filter:
            payrolls = payrolls.filter(reference_month=ref_month_filter)

        provider_filter = request.query_params.get("provider")
        if provider_filter:
            payrolls = payrolls.filter(provider_id=provider_filter)

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(payrolls, request, view=self)
        if paginated_queryset is not None:
            serializer = PayrollSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PayrollSerializer(payrolls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PayrollDetailAPIView(APIView):
    """
    Consulta ou atualiza os detalhes de Payout usando Serializers limitados ou serviços de refatoração.
    GET /payrolls/{id}/
    PUT /payrolls/{id}/
    PATCH /payrolls/{id}/
    DELETE /payrolls/{id}/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get_object(self, request, pk):
        from django.http import Http404

        try:
            return payroll_list_for_user(user=request.user).get(pk=pk)
        except Payroll.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        payroll = self.get_object(request, pk)
        serializer = PayrollDetailSerializer(payroll)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, instance, validated_data):
        service = PayrollService()
        service.recalculate_payroll(instance.id, **validated_data)

    def put(self, request, pk, *args, **kwargs):
        return self._update(request, pk, partial=False)

    def patch(self, request, pk, *args, **kwargs):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        instance = self.get_object(request, pk)
        serializer = PayrollUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            self.perform_update(instance, serializer.validated_data)
            instance.refresh_from_db()
            return Response(
                PayrollDetailSerializer(instance).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        instance = self.get_object(request, pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PayrollCalculateAPIView(APIView):
    """
    Cria e calcula nova folha.
    POST /payrolls/calculate/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode criar folhas de pagamento."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PayrollCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        provider_id = serializer.validated_data["provider_id"]
        try:
            provider = Provider.objects.get(id=provider_id)
            if provider.company != request.user.company:
                return Response(
                    {
                        "error": "Você não tem permissão para criar folha para este prestador."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Provider.DoesNotExist:
            return Response(
                {"error": "Prestador não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            payroll = PayrollService().create_payroll(
                provider_id=provider_id,
                reference_month=serializer.validated_data["reference_month"],
                overtime_hours_50=serializer.validated_data.get("overtime_hours_50", 0),
                holiday_hours=serializer.validated_data.get("holiday_hours", 0),
                night_hours=serializer.validated_data.get("night_hours", 0),
                late_minutes=serializer.validated_data.get("late_minutes", 0),
                absence_days=serializer.validated_data.get("absence_days", 0),
                absence_hours=serializer.validated_data.get("absence_hours", 0),
                manual_discounts=serializer.validated_data.get("manual_discounts", 0),
                notes=serializer.validated_data.get("notes", ""),
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_201_CREATED
        )


class PayrollCloseAPIView(APIView):
    """
    Fecha a folha. (DRAFT → CLOSED)
    POST /payrolls/{id}/close/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, pk, *args, **kwargs):
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode fechar folhas."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = payroll_list_for_user(user=request.user).get(pk=pk)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        if payroll.provider.company != request.user.company:
            return Response(
                {"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            payroll = PayrollService().close_payroll(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )


class PayrollMarkPaidAPIView(APIView):
    """
    Marca como paga. (CLOSED → PAID)
    POST /payrolls/{id}/mark-as-paid/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, pk, *args, **kwargs):
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode marcar como paga."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = payroll_list_for_user(user=request.user).get(pk=pk)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            payroll = PayrollService().mark_as_paid(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )


class PayrollReopenAPIView(APIView):
    """
    Reabre folha fechada. (CLOSED → DRAFT)
    POST /payrolls/{id}/reopen/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, pk, *args, **kwargs):
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin pode reabrir."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            payroll = payroll_list_for_user(user=request.user).get(pk=pk)
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            payroll = PayrollService().reopen_payroll(payroll_id=payroll.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollDetailSerializer(payroll).data, status=status.HTTP_200_OK
        )


class PayrollExportFileAPIView(APIView):
    """
    Exporta ficheiro Excel.
    GET /payrolls/{id}/export-file/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, pk, *args, **kwargs):
        from site_manage.application.commands.excel_service import ExcelService

        try:
            payroll = payroll_list_for_user(user=request.user).get(pk=pk)
            excel_service = ExcelService()
            file_content = excel_service.generate_payroll_excel(payroll)
            filename = excel_service.get_filename(payroll)

            response = HttpResponse(
                file_content.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except Payroll.DoesNotExist:
            return Response(
                {"error": "Folha não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PayrollMonthlyReportAPIView(APIView):
    """
    Relatório mensal em CSV.
    GET /payrolls/monthly-report/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        from site_manage.application.commands.report_service import ReportService

        reference_month = request.query_params.get("reference_month")

        if not reference_month:
            return Response(
                {"error": "Parâmetro reference_month é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin."}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            file_content = ReportService().generate_monthly_summary(
                company_id=request.user.company.id, reference_month=reference_month
            )
            filename = f"relatorio_mensal_{reference_month.replace('/', '-')}.csv"
            response = HttpResponse(
                file_content.getvalue(), content_type="text/csv; charset=utf-8"
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PayrollEmailReportAPIView(APIView):
    """
    Envia relatório por email.
    POST /payrolls/email-report/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        from site_manage.application.commands.report_service import ReportService

        reference_month = request.data.get("reference_month")
        email_address = request.data.get("email") or request.user.email

        if not reference_month or not email_address:
            return Response(
                {"error": "Mes e email necessarios."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Apenas Customer Admin."}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            file_content = ReportService().generate_monthly_summary(
                company_id=request.user.company.id, reference_month=reference_month
            )
            filename = f"relatorio_mensal_{reference_month.replace('/', '-')}.csv"

            success = EmailService().send_report_email(
                recipient_email=email_address,
                subject=f"Relatorio Folha - {reference_month}",
                body="Em anexo o relatorio.",
                attachment_name=filename,
                attachment_content=file_content.getvalue(),
                content_type="text/csv",
            )
            if success:
                return Response({"message": f"Enviado para {email_address}!"})
            return Response(
                {"error": "Falha ao enviar."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PayrollStatsAPIView(APIView):
    """
    Stats de status das folhas.
    GET /payrolls/stats/
    """

    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        queryset = payroll_list_for_user(user=request.user)
        return Response(
            {
                "total": queryset.count(),
                "draft": queryset.filter(status="DRAFT").count(),
                "paid": queryset.filter(status="PAID").count(),
            }
        )


# ==============================================================================
# DASHBOARD
# ==============================================================================


class DashboardView(APIView):
    """
    Dashboard protegido — apenas Customer Admin pode acessar.
    Delega as queries ao selector dashboard_stats_for_company().

    GET /dashboard/
    GET /dashboard/?period=7d|30d|90d|1y|all
    GET /dashboard/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "CUSTOMER_ADMIN":
            return Response(
                {
                    "error": "Acesso negado. Apenas Customer Admin pode acessar o dashboard."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Parse period filters
        period = request.GET.get("period", "30d")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            end = datetime.now().date()
            period_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
            days = period_map.get(period)
            start = (end - timedelta(days=days)) if days else None

        # Calcular meses no período
        months_in_range = None
        if start:
            from dateutil.relativedelta import relativedelta

            months_in_range = []
            current = start.replace(day=1)
            end_month = end.replace(day=1)
            while current <= end_month:
                months_in_range.append(current.strftime("%m/%Y"))
                current = current + relativedelta(months=1)

        # Stats via selector
        stats = dashboard_stats_for_company(company_id=user.company.id)

        # Agregação mensal
        from decimal import Decimal

        from django.db.models import Count, Sum

        company_payrolls = Payroll.objects.filter(provider__company=user.company)
        if months_in_range:
            company_payrolls = company_payrolls.filter(
                reference_month__in=months_in_range
            )

        monthly_aggregated = (
            company_payrolls.values("reference_month", "status")
            .annotate(count=Count("id"), total_value=Sum("net_value"))
            .order_by("reference_month", "status")
        )

        monthly_data = {}
        for item in monthly_aggregated:
            month = item["reference_month"]
            item_status = item["status"].lower()

            if month not in monthly_data:
                monthly_data[month] = {
                    "draft": {"count": 0, "value": 0},
                    "closed": {"count": 0, "value": 0},
                    "paid": {"count": 0, "value": 0},
                    "total_count": 0,
                    "total_value": 0,
                    "avg_value": 0,
                }

            monthly_data[month][item_status] = {
                "count": item["count"],
                "value": float(item["total_value"] or Decimal("0")),
            }
            monthly_data[month]["total_count"] += item["count"]
            monthly_data[month]["total_value"] += float(
                item["total_value"] or Decimal("0")
            )

        for month in monthly_data:
            count = monthly_data[month]["total_count"]
            if count > 0:
                monthly_data[month]["avg_value"] = (
                    monthly_data[month]["total_value"] / count
                )

        # Tendências
        trends = {
            "monthly_growth_percentage": 0,
            "period_vs_previous": {
                "payrolls_change": 0,
                "value_change": 0,
            },
        }
        sorted_months = sorted(
            monthly_data.keys(), key=lambda x: (x.split("/")[1], x.split("/")[0])
        )
        if len(sorted_months) >= 2:
            last_month = sorted_months[-1]
            prev_month = sorted_months[-2]
            last_total = sum(
                monthly_data[last_month][s]["value"]
                for s in ["draft", "closed", "paid"]
            )
            prev_total = sum(
                monthly_data[prev_month][s]["value"]
                for s in ["draft", "closed", "paid"]
            )
            last_count = monthly_data[last_month]["total_count"]
            prev_count = monthly_data[prev_month]["total_count"]
            if prev_total > 0:
                trends["monthly_growth_percentage"] = (
                    (last_total - prev_total) / prev_total
                ) * 100
                trends["period_vs_previous"]["value_change"] = (
                    (last_total - prev_total) / prev_total
                ) * 100
            if prev_count > 0:
                trends["period_vs_previous"]["payrolls_change"] = (
                    (last_count - prev_count) / prev_count
                ) * 100

        # Atividade recente
        recent_payrolls = company_payrolls.select_related("provider").order_by(
            "-created_at"
        )[:10]

        return Response(
            {
                "stats": stats,
                "monthly_aggregation": monthly_data,
                "trends": trends,
                "recent_activity": PayrollSerializer(recent_payrolls, many=True).data,
            }
        )


# ==============================================================================
# RECEIPT
# ==============================================================================


def generate_receipt(request, pk):
    """
    Simple Text Receipt for MVP.
    Kept for legacy compatibility — generates a plain-text receipt for payments.

    GET /receipt/<pk>/
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

# ==============================================================================
# TIME TRACKING VIEWS
# ==============================================================================

from site_manage.api.serializers import TimeRecordSerializer, TimeAdjustmentRequestSerializer
from site_manage.infrastructure.models import TimeRecord, TimeAdjustmentRequest
from django.db.models import Sum, Count
import calendar

class TimeRecordListCreateAPIView(APIView):
    """
    Lista ou cria Registros de Ponto para um Colaborador.
    GET /time-records/
    POST /time-records/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Em um sistema real, filtraríamos pelo provider associado ao user atual.
        # Aqui, como estamos focados na lógica, vou assumir todos os registros da company.
        if request.user.role == "PROVIDER":
            records = TimeRecord.objects.filter(provider__user=request.user)
        else:
            records = TimeRecord.objects.filter(provider__company=request.user.company)
            
        serializer = TimeRecordSerializer(records.order_by("-timestamp"), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Inject provider if not provided, assuming the current user is a provider.
        data = request.data.copy()
        if 'provider' not in data:
            if request.user.role == "PROVIDER" and hasattr(request.user, 'provider_profile'):
                data['provider'] = request.user.provider_profile.id
            else:
                return Response({"error": "Parâmetro provider é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
                
        serializer = TimeRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeAdjustmentRequestListCreateAPIView(APIView):
    """
    Lista ou cria Solicitações de Ajuste de Ponto.
    GET /time-adjustments/
    POST /time-adjustments/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role == "PROVIDER":
            requests = TimeAdjustmentRequest.objects.filter(provider__user=request.user)
        else:
            requests = TimeAdjustmentRequest.objects.filter(provider__company=request.user.company)
            
        serializer = TimeAdjustmentRequestSerializer(requests.order_by("-created_at"), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'provider' not in data:
            if request.user.role == "PROVIDER" and hasattr(request.user, 'provider_profile'):
                data['provider'] = request.user.provider_profile.id
            else:
                return Response({"error": "Parâmetro provider é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
                
        serializer = TimeAdjustmentRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleSummaryAPIView(APIView):
    """
    Retorna o sumário de horas mensais (espelho de ponto).
    GET /schedule-summary/?month=YYYY-MM
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month_str = request.query_params.get("month")
        if not month_str:
            return Response({"error": "Parâmetro 'month' (YYYY-MM) é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            year, month = map(int, month_str.split("-"))
            _, last_day = calendar.monthrange(year, month)
        except ValueError:
            return Response({"error": "Formato de data inválido. Use YYYY-MM."}, status=status.HTTP_400_BAD_REQUEST)

        # Na prática, deveríamos calcular exatamente batendo as entradas e saídas.
        # Aqui, como é um mock visual focado em agregar as informações requisitadas:
        stats = {
            "overtime_hours": "12:30",
            "undertime_hours": "03:15",
            "absence_days": 1,
            "worked_days": 18
        }
        
        return Response(stats, status=status.HTTP_200_OK)

