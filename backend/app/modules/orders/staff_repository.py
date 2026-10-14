"""Query daftar order untuk staff. Hanya baca; tidak mengubah data."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.orders.model import Order, OrderStatus
from app.modules.payments.model import Payment, PaymentStatus


class StaffOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _latest_payment_id():
        """Pembayaran terbaru per order: satu order tetap satu baris walau punya banyak payment."""
        return (
            select(Payment.id)
            .where(Payment.order_id == Order.id)
            .order_by(Payment.created_at.desc(), Payment.id.desc())
            .limit(1)
            .correlate(Order)
            .scalar_subquery()
        )

    def search(
        self,
        *,
        status: OrderStatus | None,
        payment_status: PaymentStatus | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[tuple[Order, Payment | None]], int]:
        join_on = Payment.id == self._latest_payment_id()
        filters = []
        if status is not None:
            filters.append(Order.status == status.value)
        if payment_status is not None:
            filters.append(Payment.status == payment_status.value)
        if search:
            # autoescape: karakter % dan _ dari user dianggap teks biasa, bukan wildcard.
            filters.append(
                Order.order_number.icontains(search, autoescape=True)
                | Order.customer_name.icontains(search, autoescape=True)
            )

        total = (
            self.db.scalar(
                select(func.count()).select_from(Order).outerjoin(Payment, join_on).where(*filters)
            )
            or 0
        )
        stmt = (
            select(Order, Payment)
            .outerjoin(Payment, join_on)
            .where(*filters)
            # Order.id sebagai pembeda terakhir: urutan stabil antar halaman.
            .order_by(Order.created_at.desc(), Order.id.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt)], total
