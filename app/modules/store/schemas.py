from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID

class StoreSettingsBase(BaseModel):
    store_name: str
    contact_email: Optional[str] = None
    currency: str = "ETB"
    timezone: str = "Africa/Addis_Ababa"
    is_active: bool = True
    features: Dict[str, Any] = {}

class StoreSettingsCreate(StoreSettingsBase):
    pass

class StoreSettingsUpdate(BaseModel):
    store_name: Optional[str] = None
    contact_email: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    features: Optional[Dict[str, Any]] = None

class StoreSettingsResponse(StoreSettingsBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)