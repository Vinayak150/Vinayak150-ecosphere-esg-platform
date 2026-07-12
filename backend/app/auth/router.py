from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.auth.dependencies import (
    get_auth_service,
    get_current_user,
    get_optional_refresh_token,
    require_permission,
)
from app.auth.middleware import rbac_permissions
from app.auth.permissions import PermissionCode
from app.auth.schemas import (
    AuthenticatedUser,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.service import AuthService
from app.auth.session import SessionResponse
from app.shared.utils.responses import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
    description="Authenticate a user with email and password and return JWT tokens.",
)
def login(
    request: Request,
    payload: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    tokens = auth_service.login(payload)
    return success_response(
        request,
        message="Login successful",
        data=TokenResponse.model_validate(tokens).model_dump(mode="json"),
    )


@router.post(
    "/refresh",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access and refresh token pair.",
)
def refresh_token(
    request: Request,
    payload: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    tokens = auth_service.refresh(payload.refresh_token)
    return success_response(
        request,
        message="Token refreshed successfully",
        data=TokenResponse.model_validate(tokens).model_dump(mode="json"),
    )


@router.post(
    "/logout",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Revoke refresh tokens and end the user session.",
)
def logout(
    request: Request,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Depends(get_optional_refresh_token)] = None,
    payload: RefreshTokenRequest | None = None,
) -> dict:
    token_value = refresh_token or (payload.refresh_token if payload else None)
    auth_service.logout(current_user.id, token_value)
    return success_response(request, message="Logout successful")


@router.get(
    "/me",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Return the authenticated user's profile, roles, and permissions.",
)
def get_me(
    request: Request,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    user = auth_service.get_current_user(current_user.id)
    return success_response(
        request,
        message="User profile retrieved successfully",
        data=UserResponse.model_validate(user).model_dump(mode="json"),
    )


@router.get(
    "/session",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get current session",
    description="Return the authenticated user's active session context and profile.",
    dependencies=[Depends(require_permission(PermissionCode.DASHBOARD_READ.value))],
)
@rbac_permissions(PermissionCode.DASHBOARD_READ)
def get_session(
    request: Request,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    session = auth_service.get_session(current_user)
    return success_response(
        request,
        message="Session retrieved successfully",
        data=SessionResponse.model_validate(session).model_dump(mode="json"),
    )
