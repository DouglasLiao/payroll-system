import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User, UserRole, Company
from site_manage.infrastructure.models import Provider
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

company = Company.objects.first()
email = "teste.agente@exemplo.com"

# Delete if exists
User.objects.filter(email=email).delete()
Provider.objects.filter(email=email).delete()

# Create dummy provider
provider = Provider.objects.create(
    name="",
    document="11122233344", # Dummy CPF
    role="Desenvolvedor",
    monthly_value=5000,
    email=email,
    company=company
)

user = User.objects.create_user(
    username=email,
    email=email,
    password=None,
    role=UserRole.PROVIDER,
    company=company,
    is_active=False
)
provider.user = user
provider.save()

token_generator = PasswordResetTokenGenerator()
uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
token = token_generator.make_token(user)

print(f"http://localhost:5174/invite/{uidb64}/{token}")
