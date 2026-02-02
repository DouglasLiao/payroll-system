"""
Seed script to populate initial email templates
Run with: python seed_templates.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.email_template import EmailTemplate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_templates():
    """Seed initial email templates"""

    db = SessionLocal()

    try:
        # Check if templates already exist
        existing = db.query(EmailTemplate).count()
        if existing > 0:
            logger.info(f"Templates already seeded ({existing} found). Skipping...")
            return

        # Read template files
        templates_dir = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates"
        )

        with open(os.path.join(templates_dir, "password_reset.html"), "r") as f:
            password_reset_html = f.read()

        with open(os.path.join(templates_dir, "password_reset.txt"), "r") as f:
            password_reset_txt = f.read()

        # Create password reset template
        password_reset_template = EmailTemplate(
            name="password_reset",
            subject="Redefinir sua senha - Payroll System",
            html_content=password_reset_html,
            text_content=password_reset_txt,
            variables={"variables": ["reset_url", "reset_token", "user_name"]},
        )

        db.add(password_reset_template)
        db.commit()

        logger.info("✅ Successfully seeded email templates!")
        logger.info("   - password_reset")

    except Exception as e:
        logger.error(f"❌ Error seeding templates: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_templates()
