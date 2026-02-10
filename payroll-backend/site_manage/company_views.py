from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from .models import Company, User, UserRole, PayrollConfiguration, Subscription
from .serializers import CompanySerializer, UserSerializer
from .permissions import IsSuperAdmin


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de empresas (apenas Super Admin).
    """

    queryset = Company.objects.all().order_by("name")
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_queryset(self):
        """
        Permite filtrar por status: /companies/?is_active=false
        """
        queryset = super().get_queryset()
        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            # Convert string boolean to python boolean
            if is_active.lower() in ["true", "1"]:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ["false", "0"]:
                queryset = queryset.filter(is_active=False)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == 1:
            return Response(
                {"error": "A empresa Super Admin não pode ser excluída."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """
        Aprova uma empresa pendente e ativa sua assinatura.
        POST /companies/{id}/approve/
        """
        company = self.get_object()

        if company.is_active:
            return Response(
                {"message": "Empresa já está ativa."}, status=status.HTTP_200_OK
            )

        # Ativar empresa
        company.is_active = True
        company.save()

        # Garantir que assinatura esteja ativa
        try:
            subscription = company.subscription
            if not subscription.is_active:
                subscription.is_active = True
                subscription.start_date = timezone.now().date()
                subscription.save()
        except Company.subscription.RelatedObjectDoesNotExist:
            # Criar assinatura se não existir (fallback)
            Subscription.objects.create(
                company=company, start_date=timezone.now().date(), is_active=True
            )

        # Garantir que configuração exista
        if not hasattr(company, "payroll_config"):
            PayrollConfiguration.objects.create(company=company)

        # Notify User about Approval
        try:
            from app_emails.services import EmailSender

            # Find the admin user (Customer Admin)
            admin_user = company.users.filter(role=UserRole.CUSTOMER_ADMIN).first()

            if admin_user and admin_user.email:
                sender = EmailSender()
                sender.send_email(
                    to_email=admin_user.email,
                    subject=f"Cadastro Aprovado! - {company.name}",
                    text_content=f"Olá {admin_user.first_name},\n\nParabéns! O cadastro da empresa {company.name} foi aprovado.\n\nVocê já pode acessar o sistema com seu email e senha.\n\nAtenciosamente,\nEquipe Payroll System",
                    html_content=f"""
                    <h2>Cadastro Aprovado!</h2>
                    <p>Olá <strong>{admin_user.first_name}</strong>,</p>
                    <p>Temos o prazer de informar que o cadastro da empresa <strong>{company.name}</strong> foi aprovado!</p>
                    <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0; color: #155724;"><strong>Status:</strong> Ativo</p>
                        <p style="margin: 0; color: #155724;"><strong>Plano:</strong> Trial (90 dias)</p>
                    </div>
                    <p>Você já pode acessar o sistema utilizando seu email e senha cadastrados.</p>
                    <br>
                    <a href="http://localhost:5173/login" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Acessar Sistema</a>
                    <hr>
                    <p>Atenciosamente,<br>Equipe Payroll System</p>
                    """,
                )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to send approval email: {e}")

        return Response(
            {"message": f"Empresa {company.name} aprovada com sucesso!"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        """
        Alterna o status ativo/inativo da empresa.
        POST /companies/{id}/toggle-status/
        """
        company = self.get_object()
        company.is_active = not company.is_active
        company.save()

        status_msg = "ativada" if company.is_active else "desativada"
        return Response(
            {
                "message": f"Empresa {company.name} {status_msg} com sucesso!",
                "is_active": company.is_active,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """
        Rejeita o cadastro da empresa (Deleta e notifica).
        POST /companies/{id}/reject/
        """
        company = self.get_object()

        # Notify User about Rejection
        try:
            from app_emails.services import EmailSender

            # Find the admin user (Customer Admin)
            admin_user = company.users.filter(role=UserRole.CUSTOMER_ADMIN).first()

            if admin_user and admin_user.email:
                sender = EmailSender()
                sender.send_email(
                    to_email=admin_user.email,
                    subject=f"Cadastro Reprovado - {company.name}",
                    text_content=f"Olá {admin_user.first_name},\n\nInformamos que o cadastro da empresa {company.name} foi reprovado.\n\nCaso tenha dúvidas, entre em contato com o suporte.\n\nAtenciosamente,\nEquipe Payroll System",
                    html_content=f"""
                    <h2>Cadastro Reprovado</h2>
                    <p>Olá <strong>{admin_user.first_name}</strong>,</p>
                    <p>Informamos que o cadastro da empresa <strong>{company.name}</strong> não foi aprovado.</p>
                    <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0; color: #721c24;"><strong>Status:</strong> Reprovado</p>
                    </div>
                    <p>Seus dados serão removidos de nossa base.</p>
                    <hr>
                    <p>Atenciosamente,<br>Equipe Payroll System</p>
                    """,
                )
        except Exception as e:
            logger.error(f"Failed to send rejection email: {e}")

        # Delete the company
        company.delete()

        return Response(
            {"message": f"Empresa {company.name} rejeitada e removida com sucesso!"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="create-admin")
    def create_admin(self, request, pk=None):
        """
        Cria um Customer Admin para a empresa.

        POST /companies/{id}/create-admin/

        Body:
        {
            "username": "admin@empresa.com",
            "email": "admin@empresa.com",
            "password": "senha123",
            "first_name": "João",
            "last_name": "Silva"
        }
        """
        company = self.get_object()

        # Validar dados obrigatórios
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not all([username, email, password]):
            return Response(
                {"error": "username, email e password são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verificar se username já existe
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username já existe"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Criar Customer Admin
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=request.data.get("first_name", ""),
            last_name=request.data.get("last_name", ""),
            role=UserRole.CUSTOMER_ADMIN,
            company=company,
            is_staff=False,
            is_superuser=False,
        )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def admins(self, request, pk=None):
        """
        Lista todos os Customer Admins da empresa.

        GET /companies/{id}/admins/
        """
        company = self.get_object()
        admins = User.objects.filter(company=company, role=UserRole.CUSTOMER_ADMIN)
        serializer = UserSerializer(admins, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def providers(self, request, pk=None):
        """
        Lista todos os providers da empresa.

        GET /companies/{id}/providers/
        """
        company = self.get_object()
        from .models import Provider

        providers = Provider.objects.filter(company=company)
        from .serializers import ProviderSerializer

        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data)
