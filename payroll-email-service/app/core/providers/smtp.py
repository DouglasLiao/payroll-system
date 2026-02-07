from app.core.providers.base import BaseEmailProvider
from typing import Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SMTPProvider(BaseEmailProvider):
    """SMTP email provider (Gmail, etc.)"""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        from_email: str = None,
        from_name: str = None,
        attachments: list = None,
    ) -> Dict[str, Any]:
        """Send email via SMTP"""

        from_email = from_email or settings.FROM_EMAIL
        from_name = from_name or settings.FROM_NAME

        # Create message
        message = MIMEMultipart("mixed")
        message["Subject"] = subject
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = to_email

        # Create alternative part for text/html
        msg_body = MIMEMultipart("alternative")

        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, "plain")
            msg_body.attach(part1)

        part2 = MIMEText(html_content, "html")
        msg_body.attach(part2)

        message.attach(msg_body)

        # Process attachments
        if attachments:
            import base64
            from email.mime.base import MIMEBase
            from email import encoders

            for attachment in attachments:
                try:
                    filename = attachment.get("filename")
                    content = attachment.get("content")
                    content_type = attachment.get(
                        "content_type", "application/octet-stream"
                    )

                    # Create attachment part
                    part = MIMEBase(*content_type.split("/"))
                    part.set_payload(base64.b64decode(content))
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {filename}",
                    )
                    message.attach(part)
                except Exception as e:
                    logger.error(f"Error attaching file: {e}")

        try:
            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=False,  # MailHog does not support TLS
            )

            logger.info(f"Email sent successfully to {to_email}")

            return {
                "success": True,
                "message_id": f"smtp-{to_email}",
                "provider": "smtp",
            }

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {"success": False, "error": str(e), "provider": "smtp"}

    async def check_connection(self) -> bool:
        """Check SMTP connection"""
        try:
            async with aiosmtplib.SMTP(
                hostname=self.host,
                port=self.port,
                use_tls=False,  # MailHog does not support TLS
            ) as smtp:
                await smtp.login(self.username, self.password)
            return True
        except Exception as e:
            logger.error(f"SMTP connection check failed: {e}")
            return False
