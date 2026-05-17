from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import health, upload
from app.core.config import get_settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    (settings.upload_dir / "kuep").mkdir(parents=True, exist_ok=True)
    (settings.upload_dir / "vlp").mkdir(parents=True, exist_ok=True)
    yield


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "API für die digitale Bauüberwachung im Bereich "
            "Leit- und Sicherungstechnik (LST) der Deutschen Bahn."
        ),
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router)
    application.include_router(upload.router)

    return application


app = create_app()
