import base64
from django.conf import settings
import logging
from requests import post

logger = logging.getLogger(__name__)


class EmailService:
    """Client for the Payroll Email Microservice"""

    def __init__(self):
        self.base_url = getattr(settings, "EMAIL_SERVICE_URL", "http://localhost:8001")
        self.api_key = getattr(settings, "EMAIL_SERVICE_API_KEY", "")

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
        Send an email with attachment using the microservice.

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
            # Encode attachment to base64
            if isinstance(attachment_content, str):
                attachment_content = attachment_content.encode("utf-8")

            encoded_content = base64.b64encode(attachment_content).decode("utf-8")

            payload = {
                "to": recipient_email,
                "subject": subject,
                "text_content": body,
                "html_content": f"<p>{body.replace(chr(10), '<br>')}</p>",
                "attachments": [
                    {
                        "filename": attachment_name,
                        "content": encoded_content,
                        "content_type": content_type,
                    }
                ],
            }

            headers = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Microservice is mounted at /email, not /api/v1/emails
            url = f"{self.base_url}/email/send"

            logger.info(f"Sending email to {recipient_email} via microservice at {url}")

            response = post(url, json=payload, headers=headers, timeout=10)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully. Status: {response.status_code}")
                return True
            else:
                logger.error(
                    f"Failed to send email. Status: {response.status_code}, Response: {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Error connecting to email microservice: {str(e)}")
            return False
