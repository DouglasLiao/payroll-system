from rest_framework import serializers
from users.models import User, Company, Subscription


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
    subscription_end_date = serializers.SerializerMethodField()

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
            "subscription_end_date",
            "created_at",
        ]

    def get_admin_count(self, obj):
        return obj.users.filter(role__in=["CUSTOMER_ADMIN", "SUPER_ADMIN"]).count()

    def get_provider_count(self, obj):
        # Access reverse relation from Company to Provider (defined in site_manage.models.Provider)
        # Verify if 'providers' is the related_name in Provider model
        return getattr(obj, "providers", []).count() if hasattr(obj, "providers") else 0

    def get_subscription_end_date(self, obj):
        if hasattr(obj, "subscription"):
            return obj.subscription.end_date
        return None


# ==============================================================================
# SUBSCRIPTION SERIALIZERS
# ==============================================================================


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para assinaturas"""

    plan_type_display = serializers.CharField(
        source="get_plan_type_display", read_only=True
    )
    company_name = serializers.CharField(source="company.name", read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = [
            "company",
            "created_at",
            "updated_at",
            "price",
            "max_providers",
        ]

    def get_status_display(self, obj):
        if not obj.is_active:
            return "Inativa"

        # Check expiry
        from django.utils import timezone

        if obj.end_date and obj.end_date < timezone.now().date():
            return "Expirada"

        return "Ativa"
