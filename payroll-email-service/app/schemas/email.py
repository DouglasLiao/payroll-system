from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID


class EmailSendRequest(BaseModel):
    """Request to send an email"""

    template: Optional[str] = None
    to: EmailStr
    subject: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")


class EmailBulkSendRequest(BaseModel):
    """Request to send bulk emails"""

    template: str
    recipients: List[Dict[str, Any]]


class EmailResponse(BaseModel):
    """Response after sending email"""

    id: UUID
    status: str
    message: str

    class Config:
        from_attributes = True


class EmailStatusResponse(BaseModel):
    """Email status details"""

    id: UUID
    status: str
    to: str
    subject: str
    sent_at: Optional[datetime] = None
    provider: Optional[str] = None
    provider_message_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EmailLogListResponse(BaseModel):
    """Paginated email logs"""

    total: int
    items: List[EmailStatusResponse]

    class Config:
        from_attributes = True
