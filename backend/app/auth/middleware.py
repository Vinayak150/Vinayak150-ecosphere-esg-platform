from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from app.auth.permissions import PermissionCode
from app.core.security import decode_token
from app.shared.schemas.responses import ErrorDetail, ErrorResponse, ResponseMeta

PUBLIC_API_PATHS: set[str] = {
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/health",
}

PUBLIC_API_PREFIXES: tuple[str, ...] = (
    "/docs",
    "/redoc",
    "/openapi.json",
)


def is_public_path(path: str) -> bool:
    if path in PUBLIC_API_PATHS:
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_API_PREFIXES)


def rbac_permissions(*permissions: PermissionCode) -> Callable:
    """Attach RBAC metadata to endpoints for documentation and dependency wiring."""

    def decorator(endpoint: Callable) -> Callable:
        endpoint.__rbac_permissions__ = [permission.value for permission in permissions]
        return endpoint

    return decorator


def _build_error_response(
    request: Request,
    *,
    message: str,
    code: str,
    status_code: int,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    response = ErrorResponse(
        message=message,
        error=ErrorDetail(code=code, details=None),
        meta=ResponseMeta(request_id=request_id, timestamp=datetime.now(UTC)),
    )
    return JSONResponse(status_code=status_code, content=response.model_dump(mode="json"))


def _extract_bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token


class AuthenticationRBACMiddleware(BaseHTTPMiddleware):
    """Validates JWT access tokens on protected API routes before handlers execute."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        if not path.startswith("/api/v1") or is_public_path(path):
            return await call_next(request)

        token = _extract_bearer_token(request)
        if token is None:
            return _build_error_response(
                request,
                message="Authentication credentials were not provided",
                code="UNAUTHORIZED",
                status_code=401,
            )

        try:
            payload = decode_token(token)
        except ValueError:
            return _build_error_response(
                request,
                message="Invalid or expired access token",
                code="UNAUTHORIZED",
                status_code=401,
            )

        if payload.get("type") != "access":
            return _build_error_response(
                request,
                message="Token is not an access token",
                code="UNAUTHORIZED",
                status_code=401,
            )

        try:
            user_id = UUID(payload["sub"])
        except (KeyError, ValueError):
            return _build_error_response(
                request,
                message="Invalid access token",
                code="UNAUTHORIZED",
                status_code=401,
            )

        request.state.user_id = user_id
        request.state.token_payload = payload

        return await call_next(request)
