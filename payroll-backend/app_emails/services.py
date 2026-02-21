import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.utils import timezone

from .models import EmailLog, EmailTemplate

logger = logging.getLogger(__name__)


class EmailSender:
    def send_email(
        self,
        to_email,
        subject,
        html_content,
        text_content=None,
        template_name=None,
        context=None,
        attachments=None,
        company=None,
    ):
        """
        Send an email and log it.
        """
        email_log = EmailLog.objects.create(
            to_email=to_email,
            subject=subject,
            status="pending",
            context=context,
            company=company,
        )

        if template_name:
            try:
                template = EmailTemplate.objects.get(name=template_name)
                email_log.template = template
                email_log.save()
            except EmailTemplate.DoesNotExist:
                logger.warning(
                    f"Template '{template_name}' not found. Logging but sending without template link."
                )

        try:
            # Create email object
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content or "Please enable HTML to view this email.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email],
            )

            email.attach_alternative(html_content, "text/html")

            # Handle attachments
            # attachments should be a list of dicts: {'filename': str, 'content': bytes/str, 'content_type': str}
            # or a list of tuples (filename, content, mime_type)
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, dict):
                        email.attach(
                            attachment["filename"],
                            attachment["content"],
                            attachment.get("content_type"),
                        )
                    elif isinstance(attachment, (tuple, list)) and len(attachment) >= 2:
                        email.attach(*attachment)

            # Send email
            email.send()

            # Update log
            email_log.status = "sent"
            email_log.sent_at = timezone.now()
            email_log.save()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
            email_log.status = "failed"
            email_log.error_message = str(e)
            email_log.save()
            return False

    def send_from_template(
        self, template_name, to_email, context, attachments=None, company=None
    ):
        try:
            template = EmailTemplate.objects.get(name=template_name)

            # Render fields
            subject_tmpl = Template(template.subject)
            html_tmpl = Template(template.html_content)

            ctx = Context(context)
            subject = subject_tmpl.render(ctx)
            html_content = html_tmpl.render(ctx)

            text_content = None
            if template.text_content:
                text_tmpl = Template(template.text_content)
                text_content = text_tmpl.render(ctx)

            return self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                template_name=template_name,
                context=context,
                attachments=attachments,
                company=company,
            )

        except EmailTemplate.DoesNotExist:
            logger.error(f"Template '{template_name}' not found")
            return False
        except Exception as e:
            logger.error(
                f"Error rendering template '{template_name}': {e}", exc_info=True
            )
            return False
