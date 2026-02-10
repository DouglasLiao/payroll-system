import logging
import base64
from app_emails.services import EmailSender

logger = logging.getLogger(__name__)


class EmailService:
    """
    Wrapper for the new EmailSender service to maintain backward compatibility
    with existing code that uses this class.
    """

    def __init__(self):
        self.sender = EmailSender()

    def send_report_email(
        self,
        recipient_email,
        subject,
        body,
        attachment_name,
        attachment_content,
        content_type="text/csv",
    ):
        """
        Send an email with attachment using the new monolithic email service.
        Maintains the same signature as the old microservice client.

        Args:
            recipient_email (str): Email recipient
            subject (str): Email subject
            body (str): Email body (text)
            attachment_name (str): Filename for the attachment
            attachment_content (bytes): Content of the attachment
            content_type (str): MIME type of the attachment

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare attachment for EmailSender
            # EmailSender expects attachments as list of dicts or tuples
            attachments = []
            if attachment_name and attachment_content:
                attachments.append(
                    {
                        "filename": attachment_name,
                        "content": attachment_content,
                        "content_type": content_type,
                    }
                )

            # Use html_content as body with simple wrapping, and text_content as body
            html_content = f"<p>{body.replace(chr(10), '<br>')}</p>"

            return self.sender.send_email(
                to_email=recipient_email,
                subject=subject,
                html_content=html_content,
                text_content=body,
                attachments=attachments,
            )

        except Exception as e:
            logger.error(f"Error sending email via legacy wrapper: {str(e)}")
            return False
