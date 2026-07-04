from app.core.database import AsyncSessionLocal
from app.modules.audit.models import AuditLog
from app.events.bus import event_bus
import structlog

logger = structlog.get_logger()

async def log_audit_event(
    user_id: str, 
    action: str, 
    entity_type: str, 
    entity_id: str, 
    changes: dict = None
):
    """Writes an audit log entry to the database."""
    async with AsyncSessionLocal() as db:
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                changes=changes
            )
            db.add(audit_entry)
            await db.commit()
        except Exception as e:
            logger.error("Failed to save audit log", error=str(e))

