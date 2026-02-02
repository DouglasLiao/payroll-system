from app.core.email_sender import EmailSender
from app.core.template_engine import TemplateEngine
from app.models.email_template import EmailTemplate
from app.db.session import get_db
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """High-level email service with template support"""

    def __init__(self):
        self.sender = EmailSender()
        self.template_engine = TemplateEngine()

    async def send_from_template(
        self,
        template_name: str,
        to_email: str,
        context: Dict[str, Any],
        tenant_id: Optional[str] = None,
        db_session: Session = None,
    ):
        """Render template and send email"""

        if db_session is None:
            from app.db.session import SessionLocal

            db_session = SessionLocal()
            should_close = True
        else:
            should_close = False

        try:
            # Get template from database
            template = (
                db_session.query(EmailTemplate)
                .filter(EmailTemplate.name == template_name)
                .first()
            )

            if not template:
                raise ValueError(f"Template '{template_name}' not found")

            # Render template
            subject = self.template_engine.render_string(template.subject, context)
            html_content = self.template_engine.render_string(
                template.html_content, context
            )
            text_content = None
            if template.text_content:
                text_content = self.template_engine.render_string(
                    template.text_content, context
                )

            # Send email
            return await self.sender.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                template_name=template_name,
                context=context,
                tenant_id=tenant_id,
                db_session=db_session,
            )
        finally:
            if should_close:
                db_session.close()

    async def send_direct(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        db_session: Session = None,
    ):
        """Send email directly without template"""
        return await self.sender.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            context=context,
            tenant_id=tenant_id,
            db_session=db_session,
        )
