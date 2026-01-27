# Email Service - Design Detalhado

## Overview

Microserviço dedicado para gerenciamento e envio de emails transacionais no Payroll System.

## Stack Tecnológica

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (logs e templates)
- **Cache/Queue**: Redis
- **Email Provider**: SendGrid (recomendado)
- **Template Engine**: Jinja2
- **Container**: Docker

## Estrutura do Projeto

```
payroll-email-service/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings e configurações
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── email.py        # Email endpoints
│   │   │   ├── templates.py    # Template management
│   │   │   └── health.py       # Health check
│   │   └── dependencies.py     # Shared dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── email_sender.py     # Core email sending logic
│   │   ├── template_engine.py  # Template rendering
│   │   └── providers/
│   │       ├── base.py         # Abstract base provider
│   │       ├── sendgrid.py     # SendGrid implementation
│   │       └── ses.py          # AWS SES implementation (futuro)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── email_log.py        # Email log model
│   │   └── email_template.py   # Email template model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── email.py            # Pydantic schemas
│   │   └── template.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── email_service.py    # Business logic
│   │   └── event_subscriber.py # Redis pub/sub listener
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   └── templates/
│       ├── password_reset.html
│       ├── password_reset.txt
│       ├── payroll_completed.html
│       └── welcome.html
├── tests/
│   ├── __init__.py
│   ├── test_email_service.py
│   └── test_api.py
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Database Schema

```sql
-- Email Templates
CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    subject VARCHAR(255) NOT NULL,
    html_content TEXT NOT NULL,
    text_content TEXT,
    variables JSONB,  -- Expected variables in template
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email Logs
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(100),
    to_email VARCHAR(255) NOT NULL,
    from_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- pending, sent, failed, bounced
    provider VARCHAR(50),  -- sendgrid, ses, etc
    provider_message_id VARCHAR(255),
    error_message TEXT,
    context JSONB,  -- Template variables used
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retry_count INT DEFAULT 0,
    tenant_id UUID  -- Multi-tenancy support
);

CREATE INDEX idx_email_logs_status ON email_logs(status);
CREATE INDEX idx_email_logs_tenant ON email_logs(tenant_id);
CREATE INDEX idx_email_logs_created ON email_logs(created_at DESC);
```

## API Endpoints

### Email Endpoints

#### 1. Send Individual Email

```http
POST /email/send
Content-Type: application/json
Authorization: Bearer <jwt_token>
X-Tenant-ID: <tenant_uuid>

{
  "template": "password_reset",
  "to": "user@example.com",
  "context": {
    "user_name": "João Silva",
    "reset_token": "abc123xyz",
    "reset_url": "https://payroll.com/reset?token=abc123xyz"
  },
  "priority": "high"
}

Response 202 Accepted:
{
  "id": "uuid",
  "status": "queued",
  "message": "Email queued for sending"
}
```

#### 2. Send Bulk Emails

```http
POST /email/send-bulk
Content-Type: application/json

{
  "template": "payroll_completed",
  "recipients": [
    {
      "to": "provider1@example.com",
      "context": {"name": "Provider 1", "amount": 5000}
    },
    {
      "to": "provider2@example.com",
      "context": {"name": "Provider 2", "amount": 3000}
    }
  ]
}

Response 202 Accepted:
{
  "batch_id": "uuid",
  "queued_count": 2,
  "status": "processing"
}
```

#### 3. Get Email Status

```http
GET /email/status/{email_id}

Response 200:
{
  "id": "uuid",
  "status": "sent",
  "to": "user@example.com",
  "subject": "Reset your password",
  "sent_at": "2026-01-26T21:00:00Z",
  "provider": "sendgrid",
  "provider_message_id": "msg_123"
}
```

#### 4. Get Email Logs

```http
GET /email/logs?status=sent&limit=50&offset=0

Response 200:
{
  "total": 150,
  "items": [
    {
      "id": "uuid",
      "to": "user@example.com",
      "subject": "...",
      "status": "sent",
      "sent_at": "..."
    }
  ]
}
```

### Template Endpoints

#### 1. List Templates

```http
GET /templates

Response 200:
[
  {
    "id": "uuid",
    "name": "password_reset",
    "subject": "Reset your password",
    "variables": ["user_name", "reset_url", "reset_token"]
  }
]
```

#### 2. Create Template

```http
POST /templates
Content-Type: application/json

{
  "name": "welcome_email",
  "subject": "Welcome to Payroll System",
  "html_content": "<html>...</html>",
  "text_content": "Welcome...",
  "variables": ["user_name", "company_name"]
}
```

### Health Endpoint

```http
GET /health

Response 200:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "email_provider": "connected"
}
```

## Código de Exemplo

### main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import email, templates, health
from app.services.event_subscriber import start_event_subscriber
from app.config import settings
import asyncio

app = FastAPI(title="Payroll Email Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(email.router, prefix="/email", tags=["email"])
app.include_router(templates.router, prefix="/templates", tags=["templates"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.on_event("startup")
async def startup_event():
    # Start Redis subscriber in background
    asyncio.create_task(start_event_subscriber())

@app.get("/")
async def root():
    return {"service": "email-service", "version": "1.0.0"}
```

### email_sender.py

```python
from typing import Dict, Any
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.config import settings
from app.models.email_log import EmailLog
from app.db.session import get_db

class EmailSender:
    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        template_name: str = None,
        context: Dict[str, Any] = None,
        tenant_id: str = None
    ) -> EmailLog:
        """Send email via SendGrid and log the result."""

        from_email = Email(settings.FROM_EMAIL)
        to_email_obj = To(to_email)

        # Create email
        mail = Mail(
            from_email=from_email,
            to_emails=to_email_obj,
            subject=subject,
            html_content=Content("text/html", html_content)
        )

        if text_content:
            mail.add_content(Content("text/plain", text_content))

        # Create log entry
        email_log = EmailLog(
            template_name=template_name,
            to_email=to_email,
            from_email=settings.FROM_EMAIL,
            subject=subject,
            status="pending",
            provider="sendgrid",
            context=context,
            tenant_id=tenant_id
        )

        try:
            # Send via SendGrid
            response = self.sg.send(mail)

            # Update log
            email_log.status = "sent"
            email_log.provider_message_id = response.headers.get("X-Message-Id")
            email_log.sent_at = datetime.utcnow()

        except Exception as e:
            email_log.status = "failed"
            email_log.error_message = str(e)
            email_log.retry_count += 1

        # Save to database
        async with get_db() as db:
            db.add(email_log)
            await db.commit()
            await db.refresh(email_log)

        return email_log
```

### email_service.py

```python
from app.core.email_sender import EmailSender
from app.core.template_engine import TemplateEngine
from app.models.email_template import EmailTemplate
from typing import Dict, Any

class EmailService:
    def __init__(self):
        self.sender = EmailSender()
        self.template_engine = TemplateEngine()

    async def send_from_template(
        self,
        template_name: str,
        to_email: str,
        context: Dict[str, Any],
        tenant_id: str = None
    ):
        """Render template and send email."""

        # Get template from database
        template = await EmailTemplate.get_by_name(template_name)

        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Render template
        subject = self.template_engine.render_string(template.subject, context)
        html_content = self.template_engine.render_string(template.html_content, context)
        text_content = None
        if template.text_content:
            text_content = self.template_engine.render_string(template.text_content, context)

        # Send email
        return await self.sender.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            template_name=template_name,
            context=context,
            tenant_id=tenant_id
        )
```

### event_subscriber.py

```python
import redis.asyncio as redis
import json
from app.services.email_service import EmailService
from app.config import settings

async def start_event_subscriber():
    """Subscribe to Redis events and send emails accordingly."""

    r = await redis.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe("payroll.events")

    email_service = EmailService()

    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                event = json.loads(message['data'])
                event_type = event.get('event_type')
                data = event.get('data', {})

                # Handle password reset event
                if event_type == 'user.password_reset_requested':
                    await email_service.send_from_template(
                        template_name='password_reset',
                        to_email=data['email'],
                        context={
                            'reset_token': data['token'],
                            'reset_url': f"{settings.FRONTEND_URL}/reset-password?token={data['token']}"
                        },
                        tenant_id=data.get('tenant_id')
                    )

                # Handle other events...

            except Exception as e:
                # Log error but don't crash the subscriber
                print(f"Error processing event: {e}")
```

## Templates de Email

### password_reset.html

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Reset Your Password</title>
  </head>
  <body
    style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"
  >
    <div
      style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;"
    >
      <h1 style="color: white; margin: 0;">Payroll System</h1>
    </div>

    <div
      style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;"
    >
      <h2 style="color: #333;">Redefinir Senha</h2>
      <p>Olá,</p>
      <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>
      <p>Clique no botão abaixo para criar uma nova senha:</p>

      <div style="text-align: center; margin: 30px 0;">
        <a
          href="{{ reset_url }}"
          style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; 
                      padding: 15px 30px; 
                      text-decoration: none; 
                      border-radius: 5px; 
                      display: inline-block;
                      font-weight: bold;"
        >
          Redefinir Senha
        </a>
      </div>

      <p style="color: #666; font-size: 14px;">
        Se você não solicitou a redefinição de senha, ignore este email. Este
        link expira em 1 hora.
      </p>

      <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;" />

      <p style="color: #999; font-size: 12px; text-align: center;">
        © 2026 Sistema de Payroll. Todos os direitos reservados.
      </p>
    </div>
  </body>
</html>
```

## Configuração

### requirements.txt

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sendgrid==6.11.0
redis==5.0.1
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic-settings==2.1.0
jinja2==3.1.3
python-multipart==0.0.6
httpx==0.26.0
```

### .env.example

```env
# Service Configuration
SERVICE_NAME=email-service
SERVICE_PORT=8001
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:postgres@db_email:5432/email_db

# Redis
REDIS_URL=redis://redis:6379/0

# Email Provider
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@payrollsystem.com
FROM_NAME=Payroll System

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:5173

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# JWT (for authentication)
JWT_SECRET=your_jwt_secret_here
```

## Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini .

# Run migrations and start server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Monitoramento e Logs

### Métricas a coletar:

- Total de emails enviados (por status)
- Latência de envio
- Taxa de erro por provider
- Emails na fila
- Performance de templates

### Logs estruturados:

```python
import logging
import json

def log_email_sent(email_log):
    logging.info(json.dumps({
        "event": "email_sent",
        "email_id": str(email_log.id),
        "to": email_log.to_email,
        "template": email_log.template_name,
        "status": email_log.status,
        "tenant_id": email_log.tenant_id
    }))
```

---

**Status**: 📋 Design completo - Pronto para implementação
