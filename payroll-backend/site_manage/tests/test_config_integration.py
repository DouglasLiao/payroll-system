from rest_framework.test import APITestCase
from rest_framework import status
from site_manage.api.serializers import (
    ProviderSerializer,
    PayrollConfigurationSerializer,
    PayrollConfiguration,
    PayrollMathTemplate,
)
from users.models import (
    Company,
    User,
    UserRole,
)
from decimal import Decimal


class TestPayrollConfigurationIntegration(APITestCase):
    def setUp(self):
        # Create Super Admin
        self.super_admin = User.objects.create_superuser(
            username="superadmin",
            email="super@admin.com",
            password="password123",
            role=UserRole.SUPER_ADMIN,
        )

        # Create Company & Default Config
        self.company = Company.objects.create(
            name="Test Company", cnpj="12345678901234"
        )
        self.config = PayrollConfiguration.objects.create(company=self.company)

    def test_get_configuration(self):
        """Test retrieving configuration for a company"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get(
            f"/users/payroll-configs/?company_id={self.company.id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle simple list response
        results = response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["overtime_percentage"], "50.00")  # Default

    def test_update_configuration(self):
        """Test updating configuration values"""
        self.client.force_authenticate(user=self.super_admin)

        payload = {"overtime_percentage": "100.00", "night_shift_percentage": "30.00"}

        response = self.client.patch(
            f"/users/payroll-configs/{self.config.id}/", payload
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["overtime_percentage"], "100.00")

        # Verify persistence
        self.config.refresh_from_db()
        self.assertEqual(self.config.overtime_percentage, Decimal("100.00"))

    def test_apply_template(self):
        """Test applying a template to a company"""
        self.client.force_authenticate(user=self.super_admin)

        # Create a template
        template = PayrollMathTemplate.objects.create(
            name="High Performance", overtime_percentage=Decimal("200.00")
        )

        payload = {"company_id": self.company.id, "template_id": template.id}

        response = self.client.post("/users/payroll-configs/apply-template/", payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["overtime_percentage"], "200.00")

        self.company.payroll_config.refresh_from_db()
        self.assertEqual(
            self.company.payroll_config.overtime_percentage, Decimal("200.00")
        )

    def test_cannot_update_default_template(self):
        """Test that the default template cannot be updated"""
        self.client.force_authenticate(user=self.super_admin)
        template = PayrollMathTemplate.objects.create(
            name="Padrão", is_default=True, overtime_percentage=Decimal("50.00")
        )

        payload = {"overtime_percentage": "100.00"}
        response = self.client.patch(f"/users/math-templates/{template.id}/", payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"],
            "Não é possível alterar o template padrão do sistema.",
        )

    def test_cannot_delete_default_template(self):
        """Test that the default template cannot be deleted"""
        self.client.force_authenticate(user=self.super_admin)
        template = PayrollMathTemplate.objects.create(
            name="Padrão Delete", is_default=True, overtime_percentage=Decimal("50.00")
        )

        response = self.client.delete(f"/users/math-templates/{template.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"],
            "Não é possível excluir o template padrão do sistema.",
        )
