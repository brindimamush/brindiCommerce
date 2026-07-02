from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel

DataType = TypeVar("DataType")

class SuccessResponse(BaseModel, Generic[DataType]):
    success: bool = True
    data: DataType
    message: str = "Operation successful"
    meta: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None