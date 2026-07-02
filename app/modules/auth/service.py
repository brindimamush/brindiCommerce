from sqlalchemy.ext.asyncio import AsyncSession
from app.common.service import BaseService
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserUpdate
from app.modules.auth.repository import UserRepository, user_repository
from app.core.security import get_password_hash

class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        """Override create to handle password hashing."""
        # Convert schema to dict
        user_data = obj_in.model_dump()
        
        # Remove plain text password and generate hash
        password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(password)
        
        # Create database model instance
        db_obj = self.repository.model(**user_data)
        
        # Add to database
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj

# Instantiate a singleton to be used in routes
user_service = UserService(repository=user_repository)