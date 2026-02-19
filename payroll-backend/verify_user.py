import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from users.models import User


def check_user(username):
    try:
        user = User.objects.get(username=username)
        print(f"User found: {user.username}")
        print(f"Email: {user.email}")
        print(f"Active: {user.is_active}")
        print(f"Password set: {user.has_usable_password()}")
        print(f"Check password 'password123': {user.check_password('password123')}")
    except User.DoesNotExist:
        print(f"User {username} not found")


print("--- Checking 'admin' ---")
check_user("admin")

print("\n--- Checking 'tech_admin' ---")
check_user("tech_admin")
