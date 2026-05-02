"""Focused Milestone 11 tests for compliance, security, and operations hardening."""
import asyncio

import httpx
from fastapi import FastAPI

from app.core.config import settings
from app.core.operations_middleware import RequestCorrelationMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.main import app


async def _get(asgi_app, path: str, headers: dict | None = None):
    transport = httpx.ASGITransport(app=asgi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path, headers=headers)


def test_security_headers_and_request_id_are_added_to_health_response():
    response = asyncio.run(_get(app, "/health", headers={settings.REQUEST_ID_HEADER: "trace-m11"}))

    assert response.status_code == 200
    assert response.headers[settings.REQUEST_ID_HEADER] == "trace-m11"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.json()["status"] == "healthy"


def test_readiness_probe_returns_sanitized_database_evidence():
    response = asyncio.run(_get(app, "/ready"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["checks"]["database"] == "ok"
    assert payload["checks"]["dev_endpoints_enabled"] is False
    assert "DATABASE_URL" not in str(payload)
    assert "password" not in str(payload).lower()


def test_development_endpoints_are_not_mounted_without_explicit_flag():
    assert settings.ENABLE_DEV_ENDPOINTS is False

    route_paths = {getattr(route, "path", "") for route in app.routes}

    assert "/api/v1/dev/hash" not in route_paths
    assert "/api/v1/dev/seed" not in route_paths
    assert "/api/v1/dev/topup-dev" not in route_paths


def test_operations_and_security_middleware_are_reusable_in_isolated_app():
    isolated_app = FastAPI()
    isolated_app.add_middleware(SecurityHeadersMiddleware)
    isolated_app.add_middleware(RequestCorrelationMiddleware)

    @isolated_app.get("/ping")
    def ping():
        return {"ok": True}

    response = asyncio.run(_get(isolated_app, "/ping"))

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"
