from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.dependencies import get_db
from app.modules.orders.repository import OrderRepository
from app.modules.orders.service import OrderService


def get_order_service(db: Annotated[Session, Depends(get_db)]) -> OrderService:
    settings = get_settings()
    return OrderService(
        OrderRepository(db),
        tax_rate_percent=settings.tax_rate_percent,
        max_quantity_per_item=settings.max_quantity_per_item,
    )
