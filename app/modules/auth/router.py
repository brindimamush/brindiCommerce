from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.events.bus import event_bus
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserResponse, UserRole
from app.modules.auth.service import user_service
from app.modules.auth.repository import user_repository
from app.modules.auth.dependencies import get_current_user, require_owner, require_staff

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_repository.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )
    # The user_service handles the password hashing internally
    new_user = await user_service.create(db, obj_in=user_in)
    return new_user

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await user_repository.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_staff) # Owners and Staff can view users
):
    users = await user_service.get_all(db, skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_owner) # Only Owners can change roles[cite: 1]
):
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = new_role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Trigger audit log[cite: 1]
    await event_bus.publish(
        "audit.record",
        user_id=str(current_user.id),
        action="user.role_updated",
        entity_type="User",
        entity_id=str(user.id),
        changes={"new_role": new_role.value}
    )
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user