from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health
from app.api.customer.router import router as customer_router
from app.api.staff.router import router as staff_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.db import models  # noqa: F401  (daftarkan SEMUA tabel; FK antar-tabel butuh ini)

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title="Monster Café API",
        version="0.1.0",
        # Dokumentasi interaktif dimatikan di production.
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],  # termasuk Idempotency-Key
    )
    register_exception_handlers(app)
    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(customer_router, prefix=API_PREFIX)
    app.include_router(staff_router, prefix=API_PREFIX)
    return app


app = create_app()
