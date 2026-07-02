from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "commercehub_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # 1 hour max
)

# Example Task: Sending an email notification
@celery_app.task(name="send_notification_email")
def send_notification_email(email_to: str, subject: str, body: str):
    """
    Mock background task for sending an email.
    In a real scenario, this would integrate with SMTP or an API like SendGrid.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Sending email to {email_to} with subject: {subject}")
    # Simulate email sending delay
    import time
    time.sleep(2)
    logger.info("Email sent successfully!")
    return {"status": "success", "email": email_to}