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

        return Response(
            {"message": f"Empresa {company.name} aprovada com sucesso!"},
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
