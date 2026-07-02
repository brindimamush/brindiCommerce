import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()
        
        # Bind context variables to the structured logger for this specific request
        structlog.contextvars.bind_contextvars(
            request_id=request_id, 
            path=request.url.path,
            method=request.method,
            client_ip=request.client.host if request.client else "unknown"
        )
        
        logger.info("Request started")
        
        try:
            response = await call_next(request)
            
            # Calculate performance timing
            process_time = time.time() - start_time
            
            # Inject tracking headers into the response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            logger.info(
                "Request completed", 
                status_code=response.status_code, 
                process_time=process_time
            )
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error("Request failed", error=str(e), process_time=process_time)
            raise
            
        finally:
            # Clean up context variables to prevent memory leaks in async workers
            structlog.contextvars.clear_contextvars()