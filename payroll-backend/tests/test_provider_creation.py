import pytest
from decimal import Decimal
from site_manage.serializers import ProviderSerializer
from users.models import Company


@pytest.mark.django_db
def test_provider_creation():
    print("\n" + "=" * 70)
    print("TEST: Provider Creation Validation")
    print("=" * 70)

    # Ensure a company exists
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
