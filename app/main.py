from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.container import get_container
from app.core.logger import setup_logging, get_logger
from app.core.exceptions import BaseAppError

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────
    settings = get_settings()
    setup_logging(settings.log_level)
    get_container()                     # builds & wires all dependencies once
    logger.info("Freddy AI Assistant started", extra={
        "provider": settings.llm_provider,
        "model":    settings.openai_model,
    })
    yield
    # ── Shutdown ──────────────────────────────────────────────
    logger.info("Freddy AI Assistant shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Freddy AI Assistant",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ────────────────────────────────────
    @app.exception_handler(BaseAppError)
    async def app_error_handler(request: Request, exc: BaseAppError):
        logger.error(exc.message, extra={"code": exc.code})
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        )

    # ── Routes ────────────────────────────────────────────────
    from app.api.v1.router import router as v1_router
    app.include_router(v1_router, prefix="/api/v1")

    @app.get("/healthz", tags=["Health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()