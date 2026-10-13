from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.dependencies import get_db
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.service import InventoryService
from app.modules.orders.repository import OrderRepository
from app.modules.orders.service import OrderService


def get_order_service(db: Annotated[Session, Depends(get_db)]) -> OrderService:
    settings = get_settings()
    # Order dan inventory memakai SESSION yang sama = satu transaksi.
    inventory = InventoryService(
        InventoryRepository(db),
        reservation_timeout_minutes=settings.reservation_timeout_minutes,
    )
    return OrderService(
        OrderRepository(db),
        inventory,
        tax_rate_percent=settings.tax_rate_percent,
        max_quantity_per_item=settings.max_quantity_per_item,
    )
