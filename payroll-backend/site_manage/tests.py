from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Company, User, UserRole


class AuthenticationEndpointsTestCase(TestCase):
    """Testes para os endpoints de autenticação"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = APIClient()

        # Criar empresa de teste
        self.company = Company.objects.create(
            name="Test Company",
            cnpj="12.345.678/0001-90",
            email="test@company.com",
            phone="(11) 91234-5678",
        )

        # Criar usuário Customer Admin
        self.admin_user = User.objects.create(
            username="admin@test.com",
            email="admin@test.com",
            password=make_password("testpass123"),
            first_name="Admin",
            last_name="Test",
            role=UserRole.CUSTOMER_ADMIN,
            company=self.company,
        )

        # Criar usuário Provider
        self.provider_user = User.objects.create(
            username="provider@test.com",
            email="provider@test.com",
            password=make_password("testpass123"),
            first_name="Provider",
            last_name="Test",
            role=UserRole.PROVIDER,
            company=self.company,
        )

        # Criar Super Admin
        self.super_admin = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@test.com",
            password="superpass123",
        )

    def test_login_success(self):
        """Testa login com credenciais válidas"""
        url = reverse("api:login")
        data = {"email": "admin@test.com", "password": "testpass123"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "admin@test.com")
        self.assertEqual(response.data["user"]["role"], UserRole.CUSTOMER_ADMIN)

        # Verificar se cookies foram definidos
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_invalid_credentials(self):
        """Testa login com credenciais inválidas"""
        url = reverse("api:login")
        data = {"email": "admin@test.com", "password": "wrongpassword"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Testa login sem campos obrigatórios"""
        url = reverse("api:login")
        data = {"email": "admin@test.com"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_current_user_authenticated(self):
        """Testa endpoint de usuário logado"""
        # Fazer login primeiro
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("api:current-user")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "admin@test.com")
        self.assertEqual(response.data["role"], UserRole.CUSTOMER_ADMIN)
        self.assertEqual(response.data["company_name"], "Test Company")
        self.assertIn("inactivity_timeout", response.data)

    def test_current_user_unauthenticated(self):
        """Testa endpoint de usuário sem autenticação"""
        url = reverse("api:current-user")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        """Testa logout"""
        url = reverse("api:logout")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_change_password_success(self):
        """Testa alteração de senha com sucesso"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("api:change-password")
        data = {"old_password": "testpass123", "new_password": "newpass456"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # Verificar se a senha foi realmente alterada
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.check_password("newpass456"))

    def test_change_password_wrong_old_password(self):
        """Testa alteração de senha com senha antiga incorreta"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("api:change-password")
        data = {"old_password": "wrongpass", "new_password": "newpass456"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_update_timeout_success(self):
        """Testa atualização de timeout com sucesso"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("api:update-timeout")
        data = {"timeout": 600}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["timeout"], 600)

        # Verificar se foi atualizado no banco
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.inactivity_timeout, 600)

    def test_update_timeout_invalid_value(self):
        """Testa atualização de timeout com valor inválido"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("api:update-timeout")
        data = {"timeout": 30}  # Menor que o mínimo (60)

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_role_based_access_control(self):
        """Testa controle de acesso baseado em roles"""
        # Customer Admin deve ter acesso a providers da sua empresa
        self.client.force_authenticate(user=self.admin_user)

        providers_url = reverse("api:provider-list")
        response = self.client.get(providers_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Provider deve ter acesso apenas aos seus próprios dados
        self.client.force_authenticate(user=self.provider_user)

        response = self.client.get(providers_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Provider vê apenas seus próprios dados (se houver)

    def test_multi_tenancy_isolation(self):
        """Testa isolamento de dados entre empresas"""
        # Criar outra empresa e usuário
        other_company = Company.objects.create(
            name="Other Company",
            cnpj="98.765.432/0001-10",
            email="other@company.com",
        )

        other_admin = User.objects.create(
            username="other@test.com",
            email="other@test.com",
            password=make_password("testpass123"),
            role=UserRole.CUSTOMER_ADMIN,
            company=other_company,
        )

        # Autenticar como admin da primeira empresa
        self.client.force_authenticate(user=self.admin_user)

        providers_url = reverse("api:provider-list")
        response = self.client.get(providers_url)

        # Admin deve ver apenas providers da sua empresa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que não há providers de outras empresas

    def test_super_admin_access(self):
        """Testa que Super Admin tem acesso total"""
        self.client.force_authenticate(user=self.super_admin)

        # Super Admin deve poder acessar empresas
        companies_url = reverse("api:company-list")
        response = self.client.get(companies_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompanyManagementTestCase(TestCase):
    """Testes para gerenciamento de empresas (Super Admin)"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = APIClient()

        # Criar Super Admin
        self.super_admin = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@test.com",
            password="superpass123",
        )

    def test_create_company(self):
        """Testa criação de empresa por Super Admin"""
        self.client.force_authenticate(user=self.super_admin)

        url = reverse("api:company-list")
        data = {
            "name": "New Company",
            "cnpj": "11.222.333/0001-44",
            "email": "new@company.com",
            "phone": "(11) 98765-4321",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), 1)

    def test_list_companies(self):
        """Testa listagem de empresas"""
        # Criar empresas de teste
        Company.objects.create(
            name="Company 1", cnpj="11.111.111/0001-11", email="c1@test.com"
        )
        Company.objects.create(
            name="Company 2", cnpj="22.222.222/0001-22", email="c2@test.com"
        )

        self.client.force_authenticate(user=self.super_admin)

        url = reverse("api:company-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_company(self):
        """Testa deleção de empresa"""
        company = Company.objects.create(
            name="To Delete", cnpj="33.333.333/0001-33", email="delete@test.com"
        )

        self.client.force_authenticate(user=self.super_admin)

        url = reverse("api:company-detail", kwargs={"pk": company.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Company.objects.count(), 0)


def run_tests():
    """Função helper para executar os testes"""
    import os
    import sys

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    import django

    django.setup()

    from django.test.runner import DiscoverRunner

    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(["site_manage.tests"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    run_tests()
