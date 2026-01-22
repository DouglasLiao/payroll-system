from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from decimal import Decimal


# ==============================================================================
# AUTHENTICATION & AUTHORIZATION MODELS
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


# ==============================================================================
# PAYMENT MODELS
# ==============================================================================


class PaymentMethod(models.TextChoices):
    PIX = "PIX", "PIX"
    TED = "TED", "TED"
    TRANSFER = "TRANSFER", "Bank Transfer"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    CANCELLED = "CANCELLED", "Cancelled"


class Provider(models.Model):
    """
    Prestador de Serviços (Pessoa Jurídica - PJ)
    """

    name = models.CharField(max_length=255, verbose_name="Nome")
    role = models.CharField(max_length=100, verbose_name="Função/Cargo")

    # Configurações Contratuais PJ
    monthly_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Mensal Contratado",
        help_text="Valor mensal acordado no contrato PJ",
    )
    monthly_hours = models.IntegerField(
        default=220,
        verbose_name="Carga Horária Mensal",
        help_text="Horas de trabalho por mês (padrão: 220h)",
    )
    advance_enabled = models.BooleanField(
        default=True, verbose_name="Recebe Adiantamento Quinzenal"
    )
    advance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("40.00"),
        verbose_name="Percentual de Adiantamento",
        help_text="Percentual do adiantamento quinzenal (ex: 40%)",
    )
    vt_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Valor Vale Transporte",
        help_text="Valor fixo mensal do vale transporte",
    )

    # Dados de Pagamento
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.PIX,
        verbose_name="Método de Pagamento",
    )

    # Banking Details
    pix_key = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Chave PIX"
    )
    bank_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Banco"
    )
    bank_agency = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Agência"
    )
    bank_account = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Conta"
    )

    # Outros
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    # Multi-tenancy e Autenticação
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="providers",
        verbose_name="Empresa",
        help_text="Empresa proprietária deste prestador",
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="provider_profile",
        verbose_name="Usuário",
        help_text="Usuário associado ao prestador (para login)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Prestador"
        verbose_name_plural = "Prestadores"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Payment(models.Model):
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="payments"
    )
    reference = models.CharField(max_length=50, help_text="e.g. 01/2026")

    amount_base = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounts = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_calculated = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False
    )

    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )

    paid_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate total before saving
        self.total_calculated = (
            (self.amount_base or Decimal(0))
            + (self.bonus or Decimal(0))
            - (self.discounts or Decimal(0))
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider.name} - {self.reference} ({self.status})"


# ==============================================================================
# FOLHA DE PAGAMENTO PJ
# ==============================================================================


class PayrollStatus(models.TextChoices):
    """Status da folha de pagamento"""

    DRAFT = "DRAFT", "Rascunho"
    CLOSED = "CLOSED", "Fechada"
    PAID = "PAID", "Paga"


class Payroll(models.Model):
    """
    Folha de Pagamento para Prestador PJ

    Este modelo armazena os dados de uma folha de pagamento mensal,
    incluindo horas trabalhadas, extras, descontos e valores calculados.
    """

    # Identificação
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="payrolls",
        verbose_name="Prestador",
    )
    reference_month = models.CharField(
        max_length=7,
        verbose_name="Mês de Referência",
        help_text="Formato: MM/YYYY (ex: 01/2026)",
    )

    # Valores Base
    base_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Base Mensal",
        help_text="Valor mensal do contrato",
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name="Valor por Hora",
        help_text="Calculado automaticamente",
    )

    # Adiantamento
    advance_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Adiantamento Quinzenal",
    )
    remaining_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name="Saldo Após Adiantamento",
        help_text="Calculado automaticamente",
    )

    # Horas Trabalhadas (Extras/Especiais)
    overtime_hours_50 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas Extras 50%",
        help_text="Horas extras com 50% de adicional",
    )
    holiday_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas em Feriados",
        help_text="Horas trabalhadas em feriados (100% adicional)",
    )
    night_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas Noturnas",
        help_text="Horas com adicional noturno (20%)",
    )

    # Descontos Variáveis
    late_minutes = models.IntegerField(
        default=0,
        verbose_name="Minutos de Atraso",
        help_text="Total de minutos de atraso no mês",
    )
    absence_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas de Falta",
    )
    manual_discounts = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Descontos Manuais",
        help_text="Outros descontos a serem aplicados",
    )
    vt_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Vale Transporte",
        help_text="Valor mensal do VT",
    )

    # Valores Calculados - Proventos
    overtime_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Valor Horas Extras",
    )
    holiday_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Valor Feriados",
    )
    dsr_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="DSR",
    )
    night_shift_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Adicional Noturno",
    )
    total_earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Total de Proventos",
    )

    # Valores Calculados - Descontos
    late_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Desconto Atrasos",
    )
    absence_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Desconto Faltas",
    )
    # dsr_on_absences REMOVIDO - conceito CLT, não aplicável para PJ
    total_discounts = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Total de Descontos",
    )

    # Valores Finais
    gross_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Valor Bruto",
    )
    net_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Valor Líquido",
    )

    # Status e Controle
    status = models.CharField(
        max_length=20,
        choices=PayrollStatus.choices,
        default=PayrollStatus.DRAFT,
        verbose_name="Status",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Observações e anotações sobre esta folha",
    )

    # Datas
    closed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Data de Fechamento"
    )
    paid_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Data de Pagamento"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Folha de Pagamento"
        verbose_name_plural = "Folhas de Pagamento"
        unique_together = ["provider", "reference_month"]
        ordering = ["-reference_month", "provider__name"]
        indexes = [
            models.Index(fields=["provider", "reference_month"]),
            models.Index(fields=["status"]),
        ]

    def save(self, *args, **kwargs):
        """
        Calcula automaticamente todos os valores antes de salvar.
        Usa as funções da camada de domínio para garantir consistência.
        """
        from domain.payroll_calculator import calcular_folha_completa

        # Importar função de cálculo de dias
        from services.payroll_service import calcular_dias_mes

        # Calcular dias úteis e domingos/feriados do mês
        dias_uteis, domingos_feriados = calcular_dias_mes(self.reference_month)

        # Calcular todos os valores usando a função do domínio
        calculated = calcular_folha_completa(
            valor_contrato_mensal=self.base_value,
            percentual_adiantamento=(
                (self.advance_value / self.base_value * 100)
                if self.base_value > 0
                else Decimal("0")
            ),
            horas_extras=self.overtime_hours_50,
            horas_feriado=self.holiday_hours,
            horas_noturnas=self.night_hours,
            minutos_atraso=self.late_minutes,
            horas_falta=self.absence_hours,
            vale_transporte=self.vt_discount,
            descontos_manuais=self.manual_discounts,
            carga_horaria_mensal=(
                self.provider.monthly_hours if self.provider_id else 220
            ),
            dias_uteis_mes=dias_uteis,
            domingos_e_feriados_mes=domingos_feriados,
        )

        # Atribuir valores calculados
        self.hourly_rate = calculated["valor_hora"]
        self.remaining_value = calculated["saldo_pos_adiantamento"]
        self.overtime_amount = calculated["hora_extra_50"]
        self.holiday_amount = calculated["feriado_trabalhado"]
        self.night_shift_amount = calculated["adicional_noturno"]
        self.dsr_amount = calculated["dsr"]
        self.total_earnings = calculated["total_proventos"]
        self.late_discount = calculated["desconto_atraso"]
        self.absence_discount = calculated["desconto_falta"]
        # dsr_on_absences REMOVIDO - conceito CLT
        self.total_discounts = calculated["total_descontos"]
        self.gross_value = calculated["valor_bruto"]
        self.net_value = calculated["valor_liquido"]

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider.name} - {self.reference_month} (R$ {self.net_value})"


class ItemType(models.TextChoices):
    """Tipo de item da folha"""

    CREDIT = "CREDIT", "Crédito"
    DEBIT = "DEBIT", "Débito"


class PayrollItem(models.Model):
    """
    Item detalhado da folha de pagamento (para transparência)

    Permite visualizar o breakdown de cada componente da folha,
    facilitando a compreensão dos cálculos.
    """

    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Folha de Pagamento",
    )
    type = models.CharField(
        max_length=10, choices=ItemType.choices, verbose_name="Tipo"
    )
    description = models.CharField(max_length=200, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")

    class Meta:
        verbose_name = "Item da Folha"
        verbose_name_plural = "Itens da Folha"
        ordering = ["type", "description"]

    def __str__(self):
        return f"{self.description}: R$ {self.amount}"
