from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID


class EmailTemplateCreate(BaseModel):
    """Create email template"""

    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: Optional[List[str]] = None


class EmailTemplateUpdate(BaseModel):
    """Update email template"""

    subject: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    variables: Optional[List[str]] = None


class EmailTemplateResponse(BaseModel):
    """Email template response"""

    id: UUID
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
