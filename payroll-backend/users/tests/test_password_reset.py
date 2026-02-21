from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from users.models import User, PasswordResetToken


class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpassword123"
        )
        self.request_url = reverse("users_password_reset_request")
        self.confirm_url = reverse("users_password_reset_confirm")

    @patch("users.api.views.event_publisher.publish_password_reset_requested")
    def test_request_reset_valid_email(self, mock_publish):
        """Test requesting reset with valid email"""
        data = {"email": "test@example.com"}
        response = self.client.post(self.request_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check token created
        token = PasswordResetToken.objects.filter(user=self.user).first()
        self.assertIsNotNone(token)
        self.assertFalse(token.used)

        # Check Redis event published
        mock_publish.assert_called_once()
        # verify arguments call
        call_args = mock_publish.call_args
        self.assertEqual(call_args[1]["user_email"], "test@example.com")
        self.assertEqual(call_args[1]["token"], token.token)

    @patch("users.api.views.event_publisher.publish_password_reset_requested")
    def test_request_reset_invalid_email(self, mock_publish):
        """Test requesting reset with non-existent email"""
        data = {"email": "doesnotexist@example.com"}
        response = self.client.post(self.request_url, data, format="json")

        # Should still return 200 OK for security
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should NOT publish event
        mock_publish.assert_not_called()

    def test_confirm_reset_success(self):
        """Test confirming reset with valid token"""
        # Create token
        token = PasswordResetToken.objects.create(
            user=self.user,
            token="valid-token-123",
            expires_at=timezone.now() + timedelta(hours=1),
        )

        data = {
            "token": "valid-token-123",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        }

        response = self.client.post(self.confirm_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check user password updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

        # Check token marked used
        token.refresh_from_db()
        self.assertTrue(token.used)
        self.assertIsNotNone(token.used_at)

    def test_confirm_reset_invalid_token(self):
        """Test confirming with invalid token"""
        data = {
            "token": "invalid-token",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        }
        response = self.client.post(self.confirm_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_reset_expired_token(self):
        """Test confirming with expired token"""
        PasswordResetToken.objects.create(
            user=self.user,
            token="expired-token",
            expires_at=timezone.now() - timedelta(hours=1),
        )

        data = {
            "token": "expired-token",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        }
        response = self.client.post(self.confirm_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_reset_password_mismatch(self):
        """Test confirming with non-matching passwords"""
        PasswordResetToken.objects.create(
            user=self.user,
            token="valid-token",
            expires_at=timezone.now() + timedelta(hours=1),
        )

        data = {
            "token": "valid-token",
            "new_password": "passwordA",
            "new_password_confirm": "passwordB",
        }
        response = self.client.post(self.confirm_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
