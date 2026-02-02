"""
Redis utility for publishing events to email service
"""

import redis
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class RedisEventPublisher:
    """Publish events to Redis for microservices"""

    def __init__(self):
        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(redis_url, decode_responses=True)
        self.channel = "payroll.events"

    def publish(self, event_type: str, data: dict):
        """Publish an event to Redis"""
        try:
            event = {"event_type": event_type, "data": data}
            self.client.publish(self.channel, json.dumps(event))
            logger.info(f"Published event: {event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False

    def publish_password_reset_requested(
        self, user_email: str, token: str, user_name: str = None, tenant_id: str = None
    ):
        """Publish password reset requested event"""
        return self.publish(
            "user.password_reset_requested",
            {
                "email": user_email,
                "token": token,
                "user_name": user_name or user_email,
                "tenant_id": tenant_id,
            },
        )


# Singleton instance
event_publisher = RedisEventPublisher()
