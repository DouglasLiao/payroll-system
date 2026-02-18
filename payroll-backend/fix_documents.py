import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from site_manage.models import Provider


def generate_cpf():
    cpf = [random.randint(0, 9) for _ in range(9)]
    for _ in range(2):
        val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
        cpf.append(11 - val if val > 1 else 0)
    return "%s%s%s.%s%s%s.%s%s%s-%s%s" % tuple(cpf)


providers = Provider.objects.filter(document__isnull=True) | Provider.objects.filter(
    document=""
)
count = providers.count()

print(f"Found {count} providers with missing documents.")

for provider in providers:
    provider.document = generate_cpf()
    provider.vt_fare = "4.60"  # Also fixing bad fare just in case for older ones
    provider.save()
    print(f"Updated {provider.name}: {provider.document}")

print("Done!")
