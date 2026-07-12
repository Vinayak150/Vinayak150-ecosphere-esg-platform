from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.shared.exceptions.base import EcoSphereException
from app.shared.schemas.responses import ErrorDetail, ErrorResponse, ResponseMeta

logger = get_logger(__name__)


def _build_meta(request: Request) -> ResponseMeta:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return ResponseMeta(request_id=request_id, timestamp=datetime.now(UTC))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EcoSphereException)
    async def ecosphere_exception_handler(
        request: Request, exc: EcoSphereException
    ) -> JSONResponse:
        meta = _build_meta(request)
        response = ErrorResponse(
            message=exc.message,
            error=ErrorDetail(code=exc.code, details=exc.details),
            meta=meta,
        )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        meta = _build_meta(request)
        details: list[dict[str, Any]] = [
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        response = ErrorResponse(
            message="Validation failed",
            error=ErrorDetail(code="VALIDATION_ERROR", details=details),
            meta=meta,
        )
        return JSONResponse(status_code=400, content=response.model_dump(mode="json"))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        meta = _build_meta(request)
        response = ErrorResponse(
            message=str(exc.detail),
            error=ErrorDetail(code="HTTP_ERROR", details=None),
            meta=meta,
        )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)
        meta = _build_meta(request)
        response = ErrorResponse(
            message="Internal server error",
            error=ErrorDetail(code="INTERNAL_SERVER_ERROR", details=None),
            meta=meta,
        )
        return JSONResponse(status_code=500, content=response.model_dump(mode="json"))
