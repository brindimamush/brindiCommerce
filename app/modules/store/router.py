from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.modules.auth.dependencies import require_staff
from app.modules.store.models import StoreSettings
from app.modules.store.schemas import StoreSettingsUpdate, StoreSettingsResponse
from app.events.bus import event_bus

router = APIRouter(prefix="/store", tags=["Store Settings"])

@router.get("/", response_model=StoreSettingsResponse)
async def get_store_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreSettings).limit(1))
    settings = result.scalars().first()
    if not settings:
        # Auto-initialize if it doesn't exist to ensure a single source of truth
        settings = StoreSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings

@router.put("/", response_model=StoreSettingsResponse)
async def update_store_settings(
    settings_in: StoreSettingsUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_staff) # Only STAFF or OWNER can update
):
    result = await db.execute(select(StoreSettings).limit(1))
    settings = result.scalars().first()
    
    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
        
    db.add(settings)
    await db.commit()
    await db.refresh(settings)

    await event_bus.publish(
        "audit.record",
        user_id=str(current_user.id),
        action="store.updated",
        entity_type="StoreSettings",
        entity_id=str(settings.id),
        changes=update_data
    )
    
    return settings