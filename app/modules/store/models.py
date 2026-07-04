import uuid
from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.base_model import Base

class StoreSettings(Base):
    __tablename__ = "store_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_name = Column(String, nullable=False, default="CommerceHub Store")
    contact_email = Column(String, nullable=True)
    currency = Column(String, default="ETB")
    timezone = Column(String, default="Africa/Addis_Ababa")
    is_active = Column(Boolean, default=True)
    features = Column(JSON, default={}) # Toggle specific UI/Bot features