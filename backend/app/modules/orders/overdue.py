"""Deteksi order OVERDUE (spec: Overdue Detection). READY yang tidak diambil melewati batas
waktu menjadi OVERDUE + riwayat status. Order TIDAK dibatalkan dan pickup tetap bisa
dilakukan; staf mengikuti SOP. Idempotent: yang sudah OVERDUE tidak diproses lagi."""

import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import OrderStatus
from app.modules.orders.repository import OrderRepository

logger = logging.getLogger(__name__)


class OrderOverdueService:
    def __init__(self, orders: OrderRepository, *, overdue_minutes: int) -> None:
        self.orders = orders
        self.overdue_minutes = overdue_minutes

    def mark_due(self, now: datetime, *, batch_size: int = 50) -> int:
        """Tandai order yang lewat batas. Mengembalikan jumlah order yang diubah."""
        cutoff = now - timedelta(minutes=self.overdue_minutes)
        done = 0
        for order_id in self.orders.due_overdue_order_ids(cutoff, batch_size):
            if self._mark(order_id, cutoff):
                done += 1
        return done

    def _mark(self, order_id: uuid.UUID, cutoff: datetime) -> bool:
        try:
            if not self.orders.mark_overdue(order_id, cutoff):
                self.orders.rollback()  # sudah diambil / berubah di tengah jalan: lewati
                return False
            self.orders.add(
                OrderStatusHistory(
                    order_id=order_id,
                    from_status=OrderStatus.READY.value,
                    to_status=OrderStatus.OVERDUE.value,
                    changed_by=None,  # sistem
                    reason=f"Order siap tidak diambil lebih dari {self.overdue_minutes} menit",
                )
            )
            self.orders.commit()
            return True
        except Exception:
            self.orders.rollback()
            logger.exception("Gagal menandai order %s sebagai OVERDUE", order_id)
            return False


def build_overdue_service(db: Session) -> OrderOverdueService:
    return OrderOverdueService(
        OrderRepository(db), overdue_minutes=get_settings().pickup_overdue_minutes
    )
