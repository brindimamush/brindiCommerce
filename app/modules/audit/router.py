from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from app.core.database import get_db
from app.modules.auth.dependencies import require_owner
from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_owner) # Strict access[cite: 1]
):
    result = await db.execute(
        select(AuditLog).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
    )
    return result.scalars().all()