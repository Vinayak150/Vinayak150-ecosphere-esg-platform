from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.auth.middleware import AuthenticationRBACMiddleware
from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.modules.dashboard.router import router as dashboard_router
from app.modules.environmental.router import router as environmental_router
from app.modules.gamification.router import router as gamification_router
from app.modules.governance.router import router as governance_router
from app.modules.social.router import router as social_router
from app.shared.exceptions.handlers import register_exception_handlers
from app.shared.middleware.request_context import RequestContextMiddleware
from app.shared.schemas.responses import HealthData
from app.shared.utils.responses import success_response

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    yield


def create_app() -> FastAPI:
    docs_url = "/docs" if settings.environment != "production" else None
    redoc_url = "/redoc" if settings.environment != "production" else None
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="EcoSphere Enterprise ESG Management Platform API",
        docs_url=docs_url,
        redoc_url=redoc_url,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(AuthenticationRBACMiddleware)

    register_exception_handlers(app)

    api_router = APIRouter(prefix=settings.api_v1_prefix)
    api_router.include_router(auth_router)
    api_router.include_router(dashboard_router)
    api_router.include_router(environmental_router)
    api_router.include_router(social_router)
    api_router.include_router(governance_router)
    api_router.include_router(gamification_router)

    @api_router.get("/health", tags=["Health"])
    def health_check(request: Request) -> dict:
        data = HealthData(
            status="healthy",
            version=settings.app_version,
            environment=settings.environment,
        )
        return success_response(
            request,
            message="Service is healthy",
            data=data.model_dump(),
        )

    app.include_router(api_router)
    return app


app = create_app()
