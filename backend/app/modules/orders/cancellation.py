"""Customer membatalkan order yang BELUM dibayar. Satu transaksi: payment FAILED, stok
dikembalikan, reservasi CANCELLED, movement RELEASE, order CANCELLED + riwayat status.
Order yang sudah dibayar butuh alur refund/otorisasi staff (belum ada) dan ditolak."""

import uuid
from datetime import UTC, datetime

from app.core.security import verify_token
from app.modules.inventory.exceptions import ReservationNotActiveError
from app.modules.inventory.model import ReservationStatus
from app.modules.inventory.service import InventoryService
from app.modules.orders.cancel_schema import OrderCancelOut
from app.modules.orders.exceptions import OrderNotCancellableError, OrderNotFoundError
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order, OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.payments.repository import PaymentRepository

CANCEL_REASON = "Dibatalkan oleh customer"


class _StateChanged(Exception):
    """Order berubah di tengah jalan (mis. baru dibayar atau kedaluwarsa)."""


class OrderCancellationService:
    def __init__(
        self, orders: OrderRepository, payments: PaymentRepository, inventory: InventoryService
    ) -> None:
        self.orders = orders
        self.payments = payments
        self.inventory = inventory

    def cancel_by_customer(self, order_id: uuid.UUID, tracking_token: str | None) -> OrderCancelOut:
        order = self.orders.get_by_id(order_id)
        # Token kosong/salah atau order tidak ada: 404 yang sama (tidak membocorkan keberadaan).
        if (
            order is None
            or not tracking_token
            or not verify_token(tracking_token, order.tracking_token_hash)
        ):
            raise OrderNotFoundError
        if order.status == OrderStatus.CANCELLED.value:
            return self._out(order)  # sudah batal (kedaluwarsa, atau tombol ditekan dua kali)
        if order.status != OrderStatus.PENDING.value:
            raise OrderNotCancellableError

        order_number = order.order_number  # ambil sekarang: objek bisa kedaluwarsa setelah commit
        now = datetime.now(UTC)
        try:
            # Urutan kunci sama dengan bayar/kedaluwarsa (payment -> stok -> reservasi -> order).
            self.payments.fail_unpaid_for_order(order_id)
            self.inventory.release_reservations(
                order_id,
                status=ReservationStatus.CANCELLED,
                at=now,
                created_by=None,
                reason=CANCEL_REASON,
            )
            if not self.orders.mark_cancelled(order_id, now):
                raise _StateChanged
            self.orders.add(
                OrderStatusHistory(
                    order_id=order_id,
                    from_status=OrderStatus.PENDING.value,
                    to_status=OrderStatus.CANCELLED.value,
                    changed_by=None,  # customer guest
                    reason=CANCEL_REASON,
                )
            )
            self.orders.commit()
        except (ReservationNotActiveError, _StateChanged):
            self.orders.rollback()
            latest = self.orders.get_by_id(order_id)
            if latest is not None and latest.status == OrderStatus.CANCELLED.value:
                return self._out(latest)  # pekerja kedaluwarsa menang duluan: hasilnya sama
            raise OrderNotCancellableError from None  # mis. baru saja dibayar
        except Exception:
            self.orders.rollback()
            raise
        return OrderCancelOut(
            order_number=order_number, status=OrderStatus.CANCELLED.value, refund_status=None
        )

    @staticmethod
    def _out(order: Order) -> OrderCancelOut:
        return OrderCancelOut(
            order_number=order.order_number, status=order.status, refund_status=None
        )
