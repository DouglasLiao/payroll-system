import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


def verify_structure():
    print("=" * 60)
    print("🏢 VERIFICAÇÃO DE ESTRUTURA DO USERS APP")
    print("=" * 60)

    try:
        print("1. Importing CompanyViewSet from users.company_views...", end=" ")
        from users.company_views import CompanyViewSet

        print("✅ OK")
        print(f"   Class: {CompanyViewSet}")
    except ImportError as e:
        print(f"❌ Error: {e}")
        return

    try:
        print("2. Checking users.views for absence of CompanyViewSet...", end=" ")
        from users import views

        if hasattr(views, "CompanyViewSet"):
            print("❌ Error: CompanyViewSet still in users.views")
        else:
            print("✅ OK")
    except ImportError as e:
        print(f"❌ Error: {e}")

    try:
        print("3. Checking users.urls configuration...", end=" ")
        from users import urls

        # This just imports it, doesn't verify routing deeply but catches basic errors
        print("✅ OK")
    except ImportError as e:
        print(f"❌ Error importing urls: {e}")


if __name__ == "__main__":
    verify_structure()
