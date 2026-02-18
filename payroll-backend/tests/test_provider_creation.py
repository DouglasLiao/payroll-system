import os
import sys
import django
from decimal import Decimal

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from site_manage.serializers import ProviderSerializer
from site_manage.models import Company


def test_provider_creation():
    print("\n" + "=" * 70)
    print("TEST: Provider Creation Validation")
    print("=" * 70)

    company = Company.objects.first()
    if not company:
        company = Company.objects.create(
            name="Test Co", cnpj="00000000000100", email="test@co.com"
        )

    # Simulate payload from frontend
    data = {
        "name": "New Provider",
        "document": "12345678901",
        "role": "Dev",
        "monthly_value": "2.000,00",
        "payment_method": "PIX",
        "pix_key": "test@pix.com",
        "vt_enabled": False,
        "vt_fare": "",  # Frontend might send empty string if disabled?
        "vt_trips_per_day": 0,
        "company": company.id,  # Serializer expects company if not read_only? No, read_only_fields = ["company"]
    }

    # Since 'company' is read_only, we don't pass it in data if we are using ModelSerializer directly without context?
    # Wait, in the ViewSet, perform_create usually injects the company.
    # Let's see how the view handles it. But first let's just check validation.

    serializer = ProviderSerializer(data=data)
    if serializer.is_valid():
        print("✅ Serializer Valid!")
        print(serializer.validated_data)
        if (
            "document" in serializer.validated_data
            and serializer.validated_data["document"] == "12345678901"
        ):
            print("✅ Document field preserved!")
        else:
            print("❌ Document field MISSING or INVALID!")
    else:
        print("❌ Serializer Invalid!")
        print(serializer.errors)


if __name__ == "__main__":
    test_provider_creation()
