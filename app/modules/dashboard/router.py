from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.modules.auth.dependencies import require_staff
from app.modules.auth.models import User
from app.modules.audit.models import AuditLog

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_staff)
):
    # Get total users[cite: 1]
    user_count = await db.scalar(select(func.count(User.id)))
    
    # Get recent system activity[cite: 1]
    recent_activity = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(5)
    )
    
    return {
        "metrics": {
            "total_users": user_count,
            # Placeholders for future modules:
            "total_orders": 0,
            "active_products": 0, 
        },
        "recent_activity": [
            {"action": log.action, "time": log.created_at} 
            for log in recent_activity.scalars().all()
        ]
    }