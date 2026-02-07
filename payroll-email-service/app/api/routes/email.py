from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.email_service import EmailService
from app.schemas.email import (
    EmailSendRequest,
    EmailBulkSendRequest,
    EmailResponse,
    EmailStatusResponse,
    EmailLogListResponse,
)
from app.models.email_log import EmailLog
from app.models.email_template import EmailTemplate
from app.core.template_engine import TemplateEngine
from typing import Optional
from uuid import UUID
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def email_dashboard(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Render HTML dashboard of sent emails"""
    logs = db.query(EmailLog).order_by(EmailLog.created_at.desc()).limit(limit).all()
    return templates.TemplateResponse(
        "email_dashboard.html", {"request": request, "logs": logs}
    )


@router.get("/preview/{email_id}", response_class=HTMLResponse)
async def preview_email(email_id: UUID, db: Session = Depends(get_db)):
    """Preview sent email (re-rendered from template)"""
    log = db.query(EmailLog).filter(EmailLog.id == email_id).first()
    if not log:
        return HTMLResponse("<h1>Email log not found</h1>", status_code=404)

    if not log.template_name:
        # Direct email - content not saved in this version
        return HTMLResponse(
            f"""
            <div style="font-family: sans-serif; padding: 20px;">
                <h1>Direct Email (No Template)</h1>
                <p><strong>Subject:</strong> {log.subject}</p>
                <p><strong>To:</strong> {log.to_email}</p>
                <hr>
                <p><em>The full HTML content for direct emails is not currently stored in the logs. Only template-based emails can be fully previewed.</em></p>
                <pre>{log.context if log.context else 'No context saved'}</pre>
            </div>
            """
        )

    # Fetch template
    template = (
        db.query(EmailTemplate).filter(EmailTemplate.name == log.template_name).first()
    )
    if not template:
        return HTMLResponse(
            f"<h1>Template '{log.template_name}' not found</h1><p>It may have been deleted.</p>",
            status_code=404,
        )

    # Render
    engine = TemplateEngine()
    try:
        html_content = engine.render_string(template.html_content, log.context or {})
        # Add a banner indicating this is a preview
        banner = """
        <div style="background: #fef3c7; color: #92400e; padding: 10px; text-align: center; border-bottom: 1px solid #d97706; font-family: sans-serif; font-size: 14px;">
            ⚠️ <strong>Preview Mode</strong>: This is a re-rendered view based on stored data.
        </div>
        """
        return HTMLResponse(banner + html_content)
    except Exception as e:
        return HTMLResponse(
            f"<h1>Error rendering template</h1><pre>{str(e)}</pre>", status_code=500
        )


@router.post("/send", response_model=EmailResponse, status_code=202)
async def send_email(request: EmailSendRequest, db: Session = Depends(get_db)):
    """Send an email"""

    email_service = EmailService()

    try:
        # If template is provided, use template
        if request.template:
            if not request.context:
                raise HTTPException(
                    status_code=400, detail="Context is required when using template"
                )

            email_log = await email_service.send_from_template(
                template_name=request.template,
                to_email=request.to,
                context=request.context,
                attachments=request.attachments,
                db_session=db,
            )
        else:
            # Direct send
            if not request.subject or not request.html_content:
                raise HTTPException(
                    status_code=400,
                    detail="Subject and html_content are required for direct send",
                )

            email_log = await email_service.send_direct(
                to_email=request.to,
                subject=request.subject,
                html_content=request.html_content,
                text_content=request.text_content,
                context=request.context,
                attachments=request.attachments,
                db_session=db,
            )

        return EmailResponse(
            id=email_log.id,
            status=email_log.status,
            message=f"Email {'sent' if email_log.status == 'sent' else 'queued'} successfully",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send email")


@router.post("/send-bulk", status_code=202)
async def send_bulk_email(request: EmailBulkSendRequest, db: Session = Depends(get_db)):
    """Send bulk emails"""

    email_service = EmailService()
    sent_count = 0
    failed_count = 0

    for recipient in request.recipients:
        try:
            await email_service.send_from_template(
                template_name=request.template,
                to_email=recipient.get("to"),
                context=recipient.get("context", {}),
                db_session=db,
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.get('to')}: {e}")
            failed_count += 1

    return {
        "total": len(request.recipients),
        "sent": sent_count,
        "failed": failed_count,
        "message": f"Bulk send completed: {sent_count} sent, {failed_count} failed",
    }


@router.get("/status/{email_id}", response_model=EmailStatusResponse)
async def get_email_status(email_id: UUID, db: Session = Depends(get_db)):
    """Get email status by ID"""

    email_log = db.query(EmailLog).filter(EmailLog.id == email_id).first()

    if not email_log:
        raise HTTPException(status_code=404, detail="Email not found")

    return EmailStatusResponse(
        id=email_log.id,
        status=email_log.status,
        to=email_log.to_email,
        subject=email_log.subject,
        sent_at=email_log.sent_at,
        provider=email_log.provider,
        provider_message_id=email_log.provider_message_id,
        error_message=email_log.error_message,
        created_at=email_log.created_at,
    )


@router.get("/logs", response_model=EmailLogListResponse)
async def get_email_logs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get email logs with pagination"""

    query = db.query(EmailLog)

    if status:
        query = query.filter(EmailLog.status == status)

    total = query.count()
    items = query.order_by(EmailLog.created_at.desc()).offset(offset).limit(limit).all()

    return EmailLogListResponse(
        total=total,
        items=[
            EmailStatusResponse(
                id=item.id,
                status=item.status,
                to=item.to_email,
                subject=item.subject,
                sent_at=item.sent_at,
                provider=item.provider,
                provider_message_id=item.provider_message_id,
                error_message=item.error_message,
                created_at=item.created_at,
            )
            for item in items
        ],
    )
