from decimal import Decimal

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone

# ==============================================================================
# COMPANY MODEL
# ==============================================================================


class Company(models.Model):
    """Empresa/Cliente do sistema"""

    name = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================================================================
# USER & AUTH MODELS
# ==============================================================================


class UserRole(models.TextChoices):
    """Roles de usuários no sistema"""

    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
    CUSTOMER_ADMIN = "CUSTOMER_ADMIN", "Customer Admin"
    PROVIDER = "PROVIDER", "Provider"


class CustomUserManager(UserManager):
    """Manager customizado para criar superusuários com role SUPER_ADMIN"""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRole.SUPER_ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    """Usuário do sistema com roles e preferências de sessão"""

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PROVIDER,
        verbose_name="Role",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        verbose_name="Empresa",
        help_text="Empresa do usuário (null para Super Admin)",
    )

    # Preferência de timeout de inatividade (em segundos)
    inactivity_timeout = models.IntegerField(
        default=300,
        verbose_name="Timeout de Inatividade",
        help_text="Tempo de inatividade antes do logout automático (segundos)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class PasswordResetToken(models.Model):
    """Token para redefinição de senha"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
        verbose_name="Usuário",
    )
    token = models.CharField(max_length=255, unique=True, verbose_name="Token")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    expires_at = models.DateTimeField(verbose_name="Expira em")
    used = models.BooleanField(default=False, verbose_name="Usado")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Usado em")

    class Meta:
        verbose_name = "Token de Reset de Senha"
        verbose_name_plural = "Tokens de Reset de Senha"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Reset token for {self.user.username}"

    def is_valid(self):
        """Verifica se o token ainda é válido"""
        return not self.used and self.expires_at > timezone.now()


# ==============================================================================
# SUBSCRIPTION MODELS
# ==============================================================================


class PlanType(models.TextChoices):
    TRIAL = "TRIAL", "Trial (90 Dias)"
    BASIC = "BASIC", "Basic (5 Prestadores)"
    PRO = "PRO", "Pro (20 Prestadores)"
    ENTERPRISE = "ENTERPRISE", "Enterprise (100 Prestadores)"
    UNLIMITED = "UNLIMITED", "Unlimited (Ilimitado)"


class Subscription(models.Model):
    """
    Assinatura e Licenciamento da Empresa.
    Controla limites de uso (número de prestadores).
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name="Empresa",
    )

    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.BASIC,
        verbose_name="Plano",
    )

    max_providers = models.IntegerField(
        verbose_name="Limite de Prestadores",
        help_text="Máximo de prestadores ativos permitidos",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço da Assinatura (R$)",
        help_text="Valor mensal cobrado",
    )

    start_date = models.DateField(verbose_name="Data de Início")
    end_date = models.DateField(
        null=True, blank=True, verbose_name="Data de Término (Null = Vitalício)"
    )

    is_active = models.BooleanField(default=True, verbose_name="Assinatura Ativa")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"

    # Defaults por plano — use SubscriptionService.create_subscription() para criar
    PLAN_DEFAULTS = {
        PlanType.TRIAL: {"max_providers": 5, "price": Decimal("0.00")},
        PlanType.BASIC: {"max_providers": 5, "price": Decimal("29.90")},
        PlanType.PRO: {"max_providers": 20, "price": Decimal("59.90")},
        PlanType.ENTERPRISE: {"max_providers": 100, "price": Decimal("99.90")},
        PlanType.UNLIMITED: {"max_providers": 999999, "price": Decimal("199.90")},
    }

    @classmethod
    def get_plan_defaults(cls, plan_type: str) -> dict:
        """Retorna os valores padrão de um plano. Use em SubscriptionService."""
        return cls.PLAN_DEFAULTS.get(plan_type, {})

    def save(self, *args, **kwargs):
        """
        Persiste a assinatura.
        NOTA: Use SubscriptionService.create_subscription() para criar assinaturas
        com defaults de plano aplicados automaticamente.
        """
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name} - {self.get_plan_type_display()}"
