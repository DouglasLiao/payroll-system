from django.db import models
from decimal import Decimal
from users.models import (
    Company,
    User,
)


# ==============================================================================
# CONFIGURATION & SUBSCRIPTION MODELS
# ==============================================================================


class TransportVoucherType(models.TextChoices):
    FIXED = "FIXED", "Valor Fixo Mensal"
    DYNAMIC_PER_DAY = "DYNAMIC_PER_DAY", "Dinâmico por Dias Trabalhados"
    DYNAMIC_PER_TRIP = "DYNAMIC_PER_TRIP", "Dinâmico por Viagem Realizada"


class BusinessDaysRule(models.TextChoices):
    WORKALENDAR = "WORKALENDAR", "Calendário Brasileiro Oficial"
    FIXED_30 = "FIXED_30", "Fixo 30 Dias"


class BasePayrollConfig(models.Model):
    """
    Modelo abstrato com as regras de cálculo de folha.
    Elimina duplicação entre PayrollMathTemplate e PayrollConfiguration.
    """

    overtime_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("50.00"),
        verbose_name="% Hora Extra",
    )
    night_shift_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        verbose_name="% Adicional Noturno",
    )
    holiday_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        verbose_name="% Feriado",
    )
    advance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("40.00"),
        verbose_name="% Adiantamento Padrão",
    )
    transport_voucher_type = models.CharField(
        max_length=20,
        choices=TransportVoucherType.choices,
        default=TransportVoucherType.DYNAMIC_PER_TRIP,
        verbose_name="Tipo de Vale Transporte",
    )
    business_days_rule = models.CharField(
        max_length=20,
        choices=BusinessDaysRule.choices,
        default=BusinessDaysRule.WORKALENDAR,
        verbose_name="Regra de Dias Úteis",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PayrollMathTemplate(BasePayrollConfig):
    """
    Templates globais de cálculos de folha.
    Permite configurar rapidamente uma empresa com regras pré-definidas.
    """

    name = models.CharField(
        max_length=100, unique=True, verbose_name="Nome do Template"
    )
    description = models.TextField(blank=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Template de Cálculo"
        verbose_name_plural = "Templates de Cálculo"

    def __str__(self):
        return self.name


class PayrollConfiguration(BasePayrollConfig):
    """
    Configuração específica de cálculo para uma empresa via OneToOne.
    Substitui as constantes globais hardcoded.
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="payroll_config",
        verbose_name="Empresa",
    )

    class Meta:
        verbose_name = "Configuração de Folha"
        verbose_name_plural = "Configurações de Folha"

    def __str__(self):
        return f"Config: {self.company.name}"


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
    document = models.CharField(
        max_length=14,
        verbose_name="CPF/CNPJ",
        null=True,
        blank=True,
        help_text="CPF (11 dígitos) ou CNPJ (14 dígitos)",
    )
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

    # Vale Transporte (Transportation Voucher) - Dynamic Configuration
    vt_enabled = models.BooleanField(
        default=False,
        verbose_name="Recebe Vale Transporte",
        help_text="Se True, VT será calculado automaticamente com base nos dias trabalhados",
    )
    vt_fare = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("4.60"),
        verbose_name="Tarifa da Passagem",
        help_text="Valor da passagem de ônibus (ex: R$ 4,60 em Belém)",
    )
    vt_trips_per_day = models.IntegerField(
        default=4,
        verbose_name="Viagens por Dia",
        help_text="Número de viagens de ônibus por dia (ex: 2, 4, 6, etc.)",
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

    # Salário Proporcional (opcional - para admissões no meio do mês)
    hired_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Admissão/Início no Mês",
        help_text="Se preenchido, calcula salário proporcional aos dias trabalhados",
    )
    worked_days = models.IntegerField(
        default=0,
        editable=False,
        verbose_name="Dias Trabalhados",
        help_text="Calculado automaticamente se hired_date preenchido (0 = mês completo)",
    )
    proportional_base_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Salário Base Proporcional",
        help_text="Calculado automaticamente se hired_date preenchido",
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

    # Faltas e Descontos Variáveis
    late_minutes = models.IntegerField(
        default=0,
        verbose_name="Minutos de Atraso",
        help_text="Total de minutos de atraso no mês",
    )
    absence_days = models.IntegerField(
        default=0,
        verbose_name="Dias de Falta",
        help_text="Número de dias de falta no mês (para cálculo de VT e desconto)",
    )
    absence_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas de Falta",
        help_text="DEPRECATED: Use absence_days. Mantido para compatibilidade.",
    )
    manual_discounts = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Descontos Manuais",
        help_text="Outros descontos a serem aplicados",
    )

    # Vale Transporte (calculated)
    vt_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Vale Transporte Calculado",
        help_text="Calculado automaticamente: viagens × tarifa × dias trabalhados",
    )
    vt_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Desconto Vale Transporte",
        help_text="DEPRECATED: Use vt_value. Mantido para compatibilidade.",
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
            # Índices otimizados para dashboard
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["reference_month", "status"]),
            models.Index(fields=["-created_at"]),  # Para recent_activity
        ]

    def save(self, *args, **kwargs):
        """
        Persiste a folha de pagamento.
        NOTA: Os cálculos são realizados pelo PayrollService antes de chamar save().
        Não coloque lógica de negócio aqui — use PayrollService.create_payroll()
        ou PayrollService.recalculate_payroll().
        """
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
