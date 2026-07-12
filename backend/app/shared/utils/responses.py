from datetime import UTC, datetime
from typing import Any

from fastapi import Request

from app.shared.schemas.responses import ResponseMeta, SuccessResponse


def build_meta(request: Request) -> ResponseMeta:
    return ResponseMeta(
        request_id=getattr(request.state, "request_id", ""),
        timestamp=datetime.now(UTC),
    )


def success_response(
    request: Request,
    *,
    message: str,
    data: Any = None,
) -> dict[str, Any]:
    response = SuccessResponse(
        message=message,
        data=data,
        meta=build_meta(request),
    )
    return response.model_dump(mode="json")
