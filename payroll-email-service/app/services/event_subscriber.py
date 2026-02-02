import redis.asyncio as redis
import json
import asyncio
from app.services.email_service import EmailService
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def start_event_subscriber():
    """Subscribe to Redis events and send emails accordingly"""

    logger.info("Starting Redis event subscriber...")

    try:
        r = await redis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe("payroll.events")

        email_service = EmailService()

        logger.info("Subscribed to payroll.events channel")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    event = json.loads(message["data"])
                    event_type = event.get("event_type")
                    data = event.get("data", {})

                    logger.info(f"Received event: {event_type}")

                    # Handle password reset event
                    if event_type == "user.password_reset_requested":
                        await email_service.send_from_template(
                            template_name="password_reset",
                            to_email=data["email"],
                            context={
                                "reset_token": data["token"],
                                "reset_url": f"{settings.FRONTEND_URL}/reset-password?token={data['token']}",
                                "user_name": data.get("user_name", "User"),
                            },
                            tenant_id=data.get("tenant_id"),
                        )
                        logger.info(f"Password reset email sent to {data['email']}")

                    # Handle other events (can be expanded later)
                    # elif event_type == 'payroll.completed':
                    #     ...

                except Exception as e:
                    # Log error but don't crash the subscriber
                    logger.error(f"Error processing event: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Redis subscriber error: {e}", exc_info=True)
        # Retry after a delay
        await asyncio.sleep(5)
        await start_event_subscriber()
