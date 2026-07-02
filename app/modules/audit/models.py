import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=True) # Nullable for system events
    action = Column(String, index=True, nullable=False) # e.g., "user.created", "order.deleted"
    entity_type = Column(String, index=True, nullable=False)
    entity_id = Column(String, index=True, nullable=False)
    changes = Column(JSONB, nullable=True) # Store what exactly changed
    created_at = Column(DateTime(timezone=True), server_default=func.now())