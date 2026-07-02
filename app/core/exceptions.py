from typing import Any, Dict, Optional
from fastapi import status

class CommerceException(Exception):
    """Base exception for all custom CommerceHub errors."""
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class ResourceNotFoundException(CommerceException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class ConflictException(CommerceException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)

class BusinessException(CommerceException):
    def __init__(self, message: str = "Business rule violation"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)

class AuthenticationException(CommerceException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class AuthorizationException(CommerceException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class ExternalServiceException(CommerceException):
    def __init__(self, message: str = "External service failed"):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)