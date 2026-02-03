from rest_framework import serializers
from .models import Provider, Payment, Payroll, PayrollItem, User, Company


# ==============================================================================
# AUTHENTICATION SERIALIZERS
# ==============================================================================


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuário com informações da empresa"""

    company_name = serializers.CharField(source="company.name", read_only=True)
    company_cnpj = serializers.CharField(source="company.cnpj", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_display",
            "company",
            "company_name",
            "company_cnpj",
            "inactivity_timeout",
            "created_at",
        ]
        read_only_fields = ["id", "role", "company", "created_at"]


class CompanySerializer(serializers.ModelSerializer):
    """Serializer para empresa"""

    admin_count = serializers.SerializerMethodField()
    provider_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "cnpj",
            "email",
            "phone",
            "is_active",
            "admin_count",
            "provider_count",
            "created_at",
        ]

    def get_admin_count(self, obj):
        return obj.users.filter(role="CUSTOMER_ADMIN").count()

    def get_provider_count(self, obj):
        return obj.providers.count()


# ==============================================================================
# PROVIDER SERIALIZERS
# ==============================================================================


class ProviderSerializer(serializers.ModelSerializer):
    """Serializer completo para Provider"""

    class Meta:
        model = Provider
        fields = "__all__"
        read_only_fields = ["company", "user", "created_at", "updated_at"]


class ProviderLightSerializer(serializers.ModelSerializer):
    """Serializer leve para listagens (apenas campos essenciais)"""

    class Meta:
        model = Provider
        fields = ["id", "name", "role", "monthly_value"]


# ==============================================================================
# PAYMENT SERIALIZERS (mantidos para compatibilidade)
# ==============================================================================


class PaymentSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.name", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


# ==============================================================================
# PAYROLL SERIALIZERS
# ==============================================================================


class PayrollItemSerializer(serializers.ModelSerializer):
    """Serializer para itens individuais da folha"""

    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = PayrollItem
        fields = ["id", "type", "type_display", "description", "amount"]


class PayrollSerializer(serializers.ModelSerializer):
    """
    Serializer básico para Payroll (sem itens aninhados).
    Usado para listagens.
    """

    provider_name = serializers.CharField(source="provider.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Payroll
        fields = [
            "id",
            "provider",
            "provider_name",
            "reference_month",
            # Salário proporcional
            "hired_date",
            "worked_days",
            "proportional_base_value",
            "status",
            "status_display",
            # Valores base
            "base_value",
            "hourly_rate",
            "advance_value",
            "remaining_value",
            # Horas
            "overtime_hours_50",
            "holiday_hours",
            "night_hours",
            "late_minutes",
            "absence_hours",
            # Descontos variáveis
            "manual_discounts",
            "vt_discount",
            # Valores calculados - Proventos
            "overtime_amount",
            "holiday_amount",
            "dsr_amount",
            "night_shift_amount",
            "total_earnings",
            # Valores calculados - Descontos
            "late_discount",
            "absence_discount",
            "total_discounts",
            # Totais
            "gross_value",
            "net_value",
            # Metadados
            "notes",
            "closed_at",
            "paid_at",
            "created_at",
            "updated_at",
        ]

        # Todos os campos calculados são read-only
        read_only_fields = [
            "worked_days",
            "proportional_base_value",
            "hourly_rate",
            "remaining_value",
            "overtime_amount",
            "holiday_amount",
            "dsr_amount",
            "night_shift_amount",
            "total_earnings",
            "late_discount",
            "absence_discount",
            "total_discounts",
            "gross_value",
            "net_value",
            "closed_at",
            "paid_at",
            "created_at",
            "updated_at",
        ]


class PayrollDetailSerializer(PayrollSerializer):
    """
    Serializer detalhado para Payroll (com itens aninhados e provider completo).
    Usado para visualização de detalhes.
    """

    items = PayrollItemSerializer(many=True, read_only=True)
    provider = ProviderLightSerializer(read_only=True)

    class Meta(PayrollSerializer.Meta):
        fields = PayrollSerializer.Meta.fields + ["items"]


class PayrollCreateSerializer(serializers.Serializer):
    """
    Serializer para criação de folha de pagamento via PayrollService.

    Este endpoint calcula automaticamente todos os valores da folha com base nas horas
    trabalhadas e descontos informados, usando as seguintes fórmulas:

    **Cálculos Automáticos:**

    1. **Valor/hora** = valor_contrato ÷ 220h
    2. **Adiantamento** = valor_contrato × percentual_adiantamento
    3. **Hora extra 50%** = horas × (valor_hora × 1.5)
    4. **Feriado** = horas × (valor_hora × 2.0)
    5. **DSR** = total_horas_extras × 16.67%
    6. **Adicional noturno** = horas × (valor_hora × 0.20)
    7. **Desconto atraso** = (minutos ÷ 60) × valor_hora
    8. **Desconto falta** = horas × valor_hora
    9. **DSR s/ faltas** = desconto_falta × 16.67%

    **Exemplo de Request:**
    ```json
    {
      "provider_id": 1,
      "reference_month": "01/2026",
      "overtime_hours_50": 10,
      "holiday_hours": 8,
      "night_hours": 20,
      "late_minutes": 30,
      "absence_hours": 8,
      "manual_discounts": 0,
      "notes": "Folha de janeiro"
    }
    ```

    **Exemplo de Response (201 Created):**
    ```json
    {
      "id": 1,
      "provider_name": "João Silva",
      "reference_month": "01/2026",
      "base_value": "2200.00",
      "hourly_rate": "10.00",
      "advance_value": "880.00",
      "overtime_amount": "150.00",
      "holiday_amount": "160.00",
      "dsr_amount": "25.00",
      "night_shift_amount": "40.00",
      "total_earnings": "1695.00",
      "late_discount": "5.00",
      "absence_discount": "80.00",
      "dsr_on_absences": "13.33",
      "vt_discount": "202.40",
      "total_discounts": "300.73",
      "net_value": "1394.27",
      "status": "DRAFT",
      "items": [...]
    }
    ```
    """

    provider_id = serializers.IntegerField(help_text="ID do prestador")
    reference_month = serializers.CharField(
        max_length=7, help_text="Mês de referência (formato: MM/YYYY, ex: 01/2026)"
    )

    # Horas trabalhadas (opcionais, default 0)
    overtime_hours_50 = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        required=False,
        help_text="Horas extras com 50% de adicional",
    )
    holiday_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        required=False,
        help_text="Horas trabalhadas em feriados (100% adicional)",
    )
    night_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        required=False,
        help_text="Horas com adicional noturno (20%)",
    )

    # Descontos (opcionais, default 0)
    late_minutes = serializers.IntegerField(
        default=0, required=False, help_text="Total de minutos de atraso no mês"
    )
    absence_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        required=False,
        help_text="Horas de falta",
    )
    manual_discounts = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        required=False,
        help_text="Outros descontos manuais",
    )

    # Adiantamento (opcional, calculado automaticamente se não informado)
    advance_already_paid = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        help_text="Adiantamento já pago (se não informado, calcula automaticamente)",
    )

    # Observações
    notes = serializers.CharField(
        required=False, allow_blank=True, help_text="Observações sobre esta folha"
    )

    def validate_reference_month(self, value):
        """Valida formato do mês de referência"""
        import re

        if not re.match(r"^\d{2}/\d{4}$", value):
            raise serializers.ValidationError(
                "Formato inválido. Use MM/YYYY (ex: 01/2026)"
            )
        return value

    def validate(self, data):
        """Validações gerais"""
        # Validar que horas não são negativas
        for field in [
            "overtime_hours_50",
            "holiday_hours",
            "night_hours",
            "absence_hours",
        ]:
            if data.get(field, 0) < 0:
                raise serializers.ValidationError({field: "Não pode ser negativo"})

        # Validar minutos de atraso
        if data.get("late_minutes", 0) < 0:
            raise serializers.ValidationError({"late_minutes": "Não pode ser negativo"})

        return data


class PayrollUpdateSerializer(serializers.Serializer):
    """
    Serializer para recálculo/atualização de folha (apenas campos editáveis).
    """

    overtime_hours_50 = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    holiday_hours = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    night_hours = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    late_minutes = serializers.IntegerField(required=False)
    absence_hours = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    manual_discounts = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    vt_discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    notes = serializers.CharField(required=False, allow_blank=True)
