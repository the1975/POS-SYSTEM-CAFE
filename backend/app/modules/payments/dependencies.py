from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.dependencies import get_db
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.service import InventoryService
from app.modules.orders.repository import OrderRepository
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.service import PaymentService


def get_payment_service(db: Annotated[Session, Depends(get_db)]) -> PaymentService:
    settings = get_settings()
    # Payment, order, dan inventory memakai SESSION yang sama = satu transaksi.
    inventory = InventoryService(
        InventoryRepository(db),
        reservation_timeout_minutes=settings.reservation_timeout_minutes,
    )
    return PaymentService(PaymentRepository(db), OrderRepository(db), inventory)
