from typing import Any


class EcoSphereException(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        details: Any = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationError(EcoSphereException):
    def __init__(self, message: str = "Validation failed", details: Any = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(EcoSphereException):
    def __init__(self, message: str = "Resource not found", details: Any = None) -> None:
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class PermissionDeniedError(EcoSphereException):
    def __init__(self, message: str = "Permission denied", details: Any = None) -> None:
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=403,
            details=details,
        )


class ConflictError(EcoSphereException):
    def __init__(self, message: str = "Resource conflict", details: Any = None) -> None:
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details,
        )


class UnauthorizedError(EcoSphereException):
    def __init__(self, message: str = "Unauthorized", details: Any = None) -> None:
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class BusinessRuleViolationError(EcoSphereException):
    def __init__(self, message: str = "Business rule violation", details: Any = None) -> None:
        super().__init__(
            message=message,
            code="BUSINESS_RULE_VIOLATION",
            status_code=422,
            details=details,
        )
