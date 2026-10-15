"""Kedaluwarsa reservasi stok (spec: Reservation Expiration Worker).
Per order, dalam SATU transaksi: payment yang belum lunas jadi FAILED, stok dikembalikan,
reservasi EXPIRED, movement RELEASE dicatat, order CANCELLED + riwayat status.
Idempotent: reservasi yang sudah EXPIRED tidak diproses lagi. Pembayaran yang sudah PAID
tidak pernah ikut kedaluwarsa (reservasinya sudah CONVERTED)."""

import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.inventory.exceptions import ReservationNotActiveError
from app.modules.inventory.model import ReservationStatus
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.service import InventoryService
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.payments.repository import PaymentRepository

logger = logging.getLogger(__name__)

EXPIRY_REASON = "Kedaluwarsa: batas waktu pembayaran lewat"


class _NotExpirable(Exception):
    """Order sudah tidak PENDING (anomali atau sudah ditangani proses lain): dilewati."""


class OrderExpirationService:
    def __init__(
        self, orders: OrderRepository, payments: PaymentRepository, inventory: InventoryService
    ) -> None:
        self.orders = orders
        self.payments = payments
        self.inventory = inventory

    def expire_due(self, now: datetime, *, batch_size: int = 50) -> int:
        """Kedaluwarsakan order yang lewat batas. Mengembalikan jumlah order yang diproses."""
        done = 0
        for order_id in self.inventory.due_order_ids(now, batch_size):
            if self._expire_order(order_id, now):
                done += 1
        return done

    def _expire_order(self, order_id: uuid.UUID, now: datetime) -> bool:
        try:
            # Urutan kunci sama dengan konfirmasi bayar (payment -> stok -> reservasi -> order),
            # supaya dua proses yang berebut tidak saling menunggu (deadlock).
            self.payments.fail_unpaid_for_order(order_id)
            self.inventory.release_reservations(
                order_id,
                status=ReservationStatus.EXPIRED,
                at=now,
                created_by=None,
                reason=EXPIRY_REASON,
            )
            if not self.orders.mark_cancelled(order_id, now):
                raise _NotExpirable
            self.orders.add(
                OrderStatusHistory(
                    order_id=order_id,
                    from_status=OrderStatus.PENDING.value,
                    to_status=OrderStatus.CANCELLED.value,
                    changed_by=None,  # sistem
                    reason=EXPIRY_REASON,
                )
            )
            self.orders.commit()
            return True
        except (ReservationNotActiveError, _NotExpirable):
            # Kalah balapan (mis. baru saja dibayar): batalkan semua perubahan order ini.
            self.orders.rollback()
            return False
        except Exception:
            self.orders.rollback()
            logger.exception("Gagal mengkedaluwarsakan order %s", order_id)
            return False


def build_expiration_service(db: Session) -> OrderExpirationService:
    inventory = InventoryService(
        InventoryRepository(db),
        reservation_timeout_minutes=get_settings().reservation_timeout_minutes,
    )
    return OrderExpirationService(OrderRepository(db), PaymentRepository(db), inventory)
