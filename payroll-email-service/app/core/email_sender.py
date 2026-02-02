from app.core.providers.base import BaseEmailProvider
from app.core.providers.smtp import SMTPProvider
from app.models.email_log import EmailLog
from app.db.session import get_db
from app.config import settings
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    """Core email sending logic"""

    def __init__(self):
        # Initialize provider based on config
        if settings.EMAIL_PROVIDER == "smtp":
            self.provider: BaseEmailProvider = SMTPProvider()
        else:
            raise ValueError(f"Unsupported email provider: {settings.EMAIL_PROVIDER}")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        db_session=None,
    ) -> EmailLog:
        """Send email via provider and log the result"""

        # Create log entry
        email_log = EmailLog(
            template_name=template_name,
            to_email=to_email,
            from_email=settings.FROM_EMAIL,
            subject=subject,
            status="pending",
            provider=settings.EMAIL_PROVIDER,
            context=context,
            tenant_id=tenant_id,
        )

        try:
            # Send via provider
            result = await self.provider.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )

            # Update log based on result
            if result.get("success"):
                email_log.status = "sent"
                email_log.provider_message_id = result.get("message_id")
                email_log.sent_at = datetime.utcnow()
                logger.info(f"Email sent successfully to {to_email}")
            else:
                email_log.status = "failed"
                email_log.error_message = result.get("error", "Unknown error")
                logger.error(f"Email failed to {to_email}: {email_log.error_message}")

        except Exception as e:
            email_log.status = "failed"
            email_log.error_message = str(e)
            email_log.retry_count += 1
            logger.error(f"Exception sending email to {to_email}: {e}")

        # Save to database
        if db_session is None:
            from app.db.session import SessionLocal

            db_session = SessionLocal()
            should_close = True
        else:
            should_close = False

        try:
            db_session.add(email_log)
            db_session.commit()
            db_session.refresh(email_log)
        finally:
            if should_close:
                db_session.close()

        return email_log

    async def check_provider_health(self) -> bool:
        """Check if email provider is healthy"""
        try:
            return await self.provider.check_connection()
        except Exception as e:
            logger.error(f"Provider health check failed: {e}")
            return False
