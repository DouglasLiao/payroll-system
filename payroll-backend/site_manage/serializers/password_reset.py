from rest_framework import serializers
from site_manage.models import User, PasswordResetToken


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Check if user exists"""
        if not User.objects.filter(email=value).exists():
            # Don't reveal if email exists or not for security
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""

    token = serializers.CharField(required=True, max_length=255)
    new_password = serializers.CharField(
        required=True, min_length=8, max_length=128, write_only=True
    )
    new_password_confirm = serializers.CharField(
        required=True, min_length=8, max_length=128, write_only=True
    )

    def validate(self, data):
        """Validate passwords match"""
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "As senhas não coincidem."}
            )
        return data

    def validate_token(self, value):
        """Validate token exists and is valid"""
        try:
            token_obj = PasswordResetToken.objects.get(token=value)
            if not token_obj.is_valid():
                raise serializers.ValidationError("Token inválido ou expirado.")
            self.context["token_obj"] = token_obj
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")
        return value
