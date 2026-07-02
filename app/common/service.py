from typing import Any, Generic, List, Optional, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import Base
from app.common.repository import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
        """
        Base service class to handle business logic and orchestrate repository calls.
        """
        self.repository = repository

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        return await self.repository.get(db, id)

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return await self.repository.get_all(db, skip=skip, limit=limit)

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        # Note: Business logic (like checking for duplicates) can be injected here in subclasses
        return await self.repository.create(db, obj_in)

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        # Note: Pre-update business validations go here
        return await self.repository.update(db, db_obj, obj_in)

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        # Note: Pre-delete checks (e.g., checking if an order is already shipped) go here
        return await self.repository.delete(db, id)