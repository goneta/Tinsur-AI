
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
import os
import hashlib
from datetime import datetime

from app.core.database import SessionLocal
from app.models.api_keys import ApiKey

class AgentAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # Allow health checks or docs without auth if needed
        if request.url.path in ["/", "/docs", "/openapi.json", "/health"]:
             return await call_next(request)

        # Retrieve API Key from headers
        api_key = request.headers.get("X-API-KEY")
        
        if not api_key:
            return JSONResponse(
                status_code=403,
                content={"error": "Unauthorized: Missing X-API-KEY header"}
            )

        # 1. Check if it's the shared internal secret (A2A service-to-service)
        expected_internal_key = os.getenv("A2A_INTERNAL_API_KEY", "super-secret-a2a-key")
        if api_key == expected_internal_key:
            return await call_next(request)

        # 2. Check Database for the key
        # Hash the incoming key to compare with stored hash
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        db = SessionLocal()
        try:
            db_key = db.query(ApiKey).filter(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True
            ).first()
            
            if db_key:
                # Update last used timestamp
                db_key.last_used_at = datetime.utcnow()
                db.commit()
                return await call_next(request)
        except Exception as e:
            # Fall secure: if DB fails, reject request
            print(f"Auth Middleware Error: {e}")
        finally:
            db.close()

        return JSONResponse(
            status_code=403,
            content={"error": "Unauthorized: Invalid X-API-KEY"}
        )
