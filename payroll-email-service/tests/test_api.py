import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app
from app.models.email_log import EmailLog
from datetime import datetime

client = TestClient(app)


@patch("app.api.routes.health.redis.from_url", new_callable=AsyncMock)
@patch("app.api.routes.health.EmailSender")
@patch("sqlalchemy.orm.Session.execute")
def test_health_check_mocked(mock_db_execute, mock_sender, mock_redis):
    # Mock Redis client
    mock_redis_client = AsyncMock()
    mock_redis_client.ping = AsyncMock(return_value=True)
    mock_redis_client.close = AsyncMock()

    # redis.from_url is awaited and returns the client
    mock_redis.return_value = mock_redis_client

    # Mock Email Provider
    mock_sender_instance = mock_sender.return_value
    mock_sender_instance.check_provider_health = AsyncMock(return_value=True)

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["redis"] == "connected"


@patch("app.api.routes.email.EmailService")
def test_send_email_success(MockEmailService):
    server_mock = MockEmailService.return_value

    # Setup expected return from send_direct
    mock_log = MagicMock()
    mock_log.id = "12345678-1234-5678-1234-567812345678"
    mock_log.status = "sent"

    # send_direct is async
    server_mock.send_direct = AsyncMock(return_value=mock_log)

    payload = {
        "to": "test@example.com",
        "subject": "Test Email",
        "html_content": "<p>Hello</p>",
    }

    response = client.post("/email/send", json=payload)

    # Assertions
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "sent"
    server_mock.send_direct.assert_called_once()


def test_get_email_status():
    # Testing get_email_status which queries DB directly
    mock_db = MagicMock()

    # Mock query result
    mock_log = EmailLog(
        id="11111111-1111-1111-1111-111111111111",
        to_email="test@example.com",
        subject="Test",
        status="sent",
        created_at=datetime.utcnow(),
    )

    # Setup mock chain: db.query().filter().first()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_log

    # Override dependency
    app.dependency_overrides = {}  # Clear prev
    from app.db.session import get_db

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/email/status/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 200
    assert response.json()["status"] == "sent"
    assert response.json()["to"] == "test@example.com"
