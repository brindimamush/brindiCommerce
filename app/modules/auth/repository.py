from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.repository import BaseRepository
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalars().first()

# Instantiate a singleton to be used across the app
user_repository = UserRepository()