from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import CommerceException
from app.common.responses import ErrorResponse
import structlog

logger = structlog.get_logger()

def setup_exception_handlers(app: FastAPI) -> None:
    
    @app.exception_handler(CommerceException)
    async def custom_exception_handler(request: Request, exc: CommerceException):
        logger.warning(
            "CommerceException caught", 
            error=exc.__class__.__name__, 
            message=exc.message,
            path=request.url.path
        )
        response = ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error", path=request.url.path, errors=exc.errors())
        response = ErrorResponse(
            error="ValidationException",
            message="Input validation failed",
            details={"errors": exc.errors()}
        )
        # HTTP 422 Unprocessable Entity is standard for validation errors
        return JSONResponse(
            status_code=422,
            content=response.model_dump()
        )
        
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", path=request.url.path, error=str(exc))
        response = ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred."
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump()
        )