import os
import sys
import django
from django.template.loader import render_to_string

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


def verify_templates():
    print("=" * 60)
    print("📧 VERIFICAÇÃO DE TEMPLATES DE EMAIL")
    print("=" * 60)

    templates_to_test = [
        (
            "emails/company_approved.html",
            {
                "first_name": "Douglas",
                "company_name": "Test Corp",
                "login_url": "http://localhost:5173/login",
            },
        ),
        (
            "emails/company_rejected.html",
            {"first_name": "Douglas", "company_name": "Rejected Corp"},
        ),
        (
            "emails/monthly_report.html",
            {"body": "Este é um teste\nde quebra de linha."},
        ),
    ]

    for template_name, context in templates_to_test:
        try:
            print(f"Testing {template_name}...", end=" ")
            rendered = render_to_string(template_name, context)
            if rendered:
                print("✅ OK")
                # print(rendered[:100] + "...") # Optional: print snippet
            else:
                print("❌ Empty output")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    verify_templates()
