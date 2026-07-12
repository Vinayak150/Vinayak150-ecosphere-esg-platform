from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    request_id: str
    timestamp: datetime


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T | None = None
    meta: ResponseMeta


class ErrorDetail(BaseModel):
    code: str
    details: list[Any] | dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: ErrorDetail
    meta: ResponseMeta


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: str | None = None
    sort: str | None = None
    order: str = Field(default="asc", pattern="^(asc|desc)$")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationMeta


class HealthData(BaseModel):
    status: str
    version: str
    environment: str


class TokenPayload(BaseModel):
    sub: UUID
    type: str
