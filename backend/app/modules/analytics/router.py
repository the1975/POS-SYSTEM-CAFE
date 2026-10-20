"""Endpoint laporan penjualan. Hanya ADMIN (OWNER = ADMIN di kode)."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.responses import DataResponse
from app.db.dependencies import get_db
from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.schema import PeakHourOut, SummaryOut, TopProductOut
from app.modules.analytics.service import AnalyticsService
from app.modules.users.dependencies import require_roles
from app.modules.users.model import RoleName, User

router = APIRouter(prefix="/analytics", tags=["analytics"])

AdminUser = Annotated[User, Depends(require_roles(RoleName.ADMIN))]


def get_analytics_service(db: Annotated[Session, Depends(get_db)]) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(db))


ServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]


@router.get("/summary", response_model=DataResponse[SummaryOut])
def summary(
    service: ServiceDep,
    admin: AdminUser,
    start_date: date | None = None,
    end_date: date | None = None,
):
    return DataResponse(data=service.summary(start_date, end_date))


@router.get("/products/top", response_model=DataResponse[list[TopProductOut]])
def top_products(
    service: ServiceDep,
    admin: AdminUser,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
):
    return DataResponse(data=service.top_products(start_date, end_date, limit))


@router.get("/peak-hours", response_model=DataResponse[list[PeakHourOut]])
def peak_hours(
    service: ServiceDep,
    admin: AdminUser,
    start_date: date | None = None,
    end_date: date | None = None,
):
    return DataResponse(data=service.peak_hours(start_date, end_date))
