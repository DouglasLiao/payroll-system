from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, Subscription, PlanType, PasswordResetToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "role", "company", "is_active", "is_staff"]
    list_filter = ["role", "company", "is_active", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role", "company", "inactivity_timeout")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "role",
                    "company",
                    "email",
                    "first_name",
                    "last_name",
                    "inactivity_timeout",
                ),
            },
        ),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "cnpj", "email", "phone", "is_active", "created_at"]
    search_fields = ["name", "cnpj", "email"]
    list_filter = ["is_active"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["company", "plan_type", "max_providers", "is_active", "end_date"]
    list_filter = ["plan_type", "is_active"]
    search_fields = ["company__name"]


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "expires_at", "used"]
    list_filter = ["used"]
    search_fields = ["user__username", "user__email"]
