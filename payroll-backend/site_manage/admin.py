from django.contrib import admin

from .infrastructure.models import Payment, Payroll, PayrollItem, Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "role",
        "monthly_value",
        "monthly_hours",
        "advance_enabled",
        "payment_method",
    ]
    list_filter = ["advance_enabled", "payment_method"]
    search_fields = ["name", "role", "email"]
    fieldsets = (
        ("Informações Básicas", {"fields": ("name", "role", "email", "description")}),
        (
            "Configurações Contratuais PJ",
            {
                "fields": (
                    "monthly_value",
                    "monthly_hours",
                    "advance_enabled",
                    "advance_percentage",
                    "vt_value",
                )
            },
        ),
        (
            "Dados de Pagamento",
            {
                "fields": (
                    "payment_method",
                    "pix_key",
                    "bank_name",
                    "bank_agency",
                    "bank_account",
                )
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "provider",
        "reference",
        "amount_base",
        "total_calculated",
        "status",
        "paid_at",
    ]
    list_filter = ["status", "paid_at"]
    search_fields = ["provider__name", "reference"]
    date_hierarchy = "created_at"


class PayrollItemInline(admin.TabularInline):
    model = PayrollItem
    extra = 0
    can_delete = False
    fields = ["type", "description", "amount"]
    readonly_fields = ["type", "description", "amount"]


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        "provider",
        "reference_month",
        "base_value",
        "net_value",
        "status",
        "created_at",
    ]
    list_filter = ["status", "reference_month"]
    search_fields = ["provider__name", "reference_month"]
    readonly_fields = [
        "hourly_rate",
        "remaining_value",
        "overtime_amount",
        "holiday_amount",
        "dsr_amount",
        "night_shift_amount",
        "total_earnings",
        "late_discount",
        "absence_discount",
        # 'dsr_on_absences', # REMOVIDO - conceito CLT
        "total_discounts",
        "gross_value",
        "net_value",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("Identificação", {"fields": ("provider", "reference_month", "status")}),
        (
            "Valores Base",
            {
                "fields": (
                    "base_value",
                    "hourly_rate",
                    "advance_value",
                    "remaining_value",
                )
            },
        ),
        (
            "Horas Trabalhadas",
            {
                "fields": ("overtime_hours_50", "holiday_hours", "night_hours"),
                "description": "Horas extras, feriados e noturnas (regras contratuais PJ)",
            },
        ),
        (
            "Descontos Variáveis",
            {
                "fields": (
                    "late_minutes",
                    "absence_hours",
                    "manual_discounts",
                    "vt_discount",
                )
            },
        ),
        (
            "Proventos Calculados",
            {
                "fields": (
                    "overtime_amount",
                    "holiday_amount",
                    "night_shift_amount",
                    "dsr_amount",
                    "total_earnings",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Descontos Calculados",
            {
                "fields": (
                    "late_discount",
                    "absence_discount",
                    # 'dsr_on_absences', # REMOVIDO - conceito CLT
                    "total_discounts",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Valores Finais",
            {
                "fields": ("gross_value", "net_value"),
                "description": "Valores calculados automaticamente",
            },
        ),
        (
            "Observações e Datas",
            {
                "fields": ("notes", "closed_at", "paid_at", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [PayrollItemInline]
    date_hierarchy = "created_at"

    def get_readonly_fields(self, request, obj=None):
        """Torna todos os campos readonly se a folha estiver fechada ou paga"""
        readonly = list(self.readonly_fields)
        if obj and obj.status in ["CLOSED", "PAID"]:
            return [f.name for f in obj._meta.fields if f.name != "status"]
        return readonly


@admin.register(PayrollItem)
class PayrollItemAdmin(admin.ModelAdmin):
    list_display = ["payroll", "type", "description", "amount"]
    list_filter = ["type", "payroll__status"]
    search_fields = ["payroll__provider__name", "description"]
