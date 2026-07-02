from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent browsers from MIME-sniffing a response away from the declared content-type
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking by forbidding the rendering of the page in a frame
        response.headers["X-Frame-Options"] = "DENY"
        # Enable cross-site scripting (XSS) filtering in the browser
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Enforce HTTP Strict Transport Security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response