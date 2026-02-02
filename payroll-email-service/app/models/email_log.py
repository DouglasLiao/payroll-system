from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.db.session import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(100), nullable=True)
    to_email = Column(String(255), nullable=False, index=True)
    from_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, index=True, default="pending")
    # Status: pending, sent, failed, bounced

    provider = Column(String(50), nullable=True)
    provider_message_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    context = Column(JSON, nullable=True)

    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    retry_count = Column(Integer, default=0)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    def __repr__(self):
        return f"<EmailLog(id={self.id}, to={self.to_email}, status={self.status})>"
