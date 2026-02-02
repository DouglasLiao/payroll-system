# Payroll Email Service

Microserviço de email para o Sistema de Payroll.

## Funcionalidades

- ✉️ Envio de emails transacionais
- 📧 Gestão de templates
- 📊 Logs e tracking de emails
- 🔄 Event-driven via Redis Pub/Sub
- 🔌 Provider abstraction (SMTP, SendGrid, etc.)

## Setup Rápido

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas credenciais SMTP
```

### 2. Rodar via Docker Compose (recomendado)

O serviço será iniciado automaticamente com:

```bash
docker-compose up
```

### 3. Acessar API

- Documentação: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

## API Endpoints

### Email

- `POST /email/send` - Enviar email
- `POST /email/send-bulk` - Enviar emails em lote
- `GET /email/status/{id}` - Status de email
- `GET /email/logs` - Histórico de emails

### Templates

- `GET /templates` - Listar templates
- `POST /templates` - Criar template
- `GET /templates/{name}` - Obter template
- `PUT /templates/{name}` - Atualizar template
- `DELETE /templates/{name}` - Deletar template

### Health

- `GET /health` - Status do serviço

## Configuração SMTP

### Gmail (Development)

1. Habilitar 2FA na sua conta Google
2. Gerar App Password: https://myaccount.google.com/apppasswords
3. Usar no .env:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_app_password_de_16_digitos
```

## Arquitetura

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Email Provider**: SMTP (configurável)
- **Template Engine**: Jinja2

## Development

### Rodar localmente (sem Docker)

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar migrations
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8001
```

## Event-Driven

O serviço escuta eventos do Redis channel `payroll.events`:

```python
# Exemplo de evento
{
    "event_type": "user.password_reset_requested",
    "data": {
        "email": "user@example.com",
        "token": "abc123",
        "tenant_id": "uuid"
    }
}
```

## Templates Disponíveis

- `password_reset` - Email de redefinição de senha
