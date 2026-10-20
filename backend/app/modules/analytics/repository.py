"""Query laporan. Definisi "terjual": order yang pembayarannya berstatus PAID dengan paid_at
di dalam rentang, dan order-nya tidak CANCELLED. Order yang di-refund (status pembayaran
berubah dari PAID) otomatis tidak ikut dihitung."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.orders.model import Order, OrderItem, OrderStatus
from app.modules.payments.model import Payment, PaymentStatus
from app.modules.products.model import Product


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _paid_in_range(start: datetime, end: datetime):
        """Filter bersama: order lunas di rentang [start, end) dan tidak dibatalkan."""
        paid_order_ids = select(Payment.order_id).where(
            Payment.status == PaymentStatus.PAID.value,
            Payment.paid_at >= start,
            Payment.paid_at < end,
        )
        return (Order.id.in_(paid_order_ids), Order.status != OrderStatus.CANCELLED.value)

    def summary(self, start: datetime, end: datetime) -> tuple[Decimal, int, int]:
        flt = self._paid_in_range(start, end)
        revenue, orders = self.db.execute(
            select(func.coalesce(func.sum(Order.total), 0), func.count(Order.id))
            .select_from(Order)
            .where(*flt)
        ).one()
        units = self.db.scalar(
            select(func.coalesce(func.sum(OrderItem.quantity), 0))
            .select_from(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .where(*flt)
        )
        return Decimal(str(revenue)), int(orders), int(units or 0)

    def top_products(self, start: datetime, end: datetime, limit: int) -> list:
        flt = self._paid_in_range(start, end)
        units = func.sum(OrderItem.quantity)
        revenue = func.sum(OrderItem.subtotal)
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                units.label("units_sold"),
                revenue.label("revenue"),
            )
            .select_from(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .join(Product, Product.id == OrderItem.product_id)
            .where(*flt)
            .group_by(Product.id, Product.name)
            # Urutan stabil: unit terjual, lalu omzet, lalu nama.
            .order_by(units.desc(), revenue.desc(), Product.name)
            .limit(limit)
        )
        return list(self.db.execute(stmt))

    def paid_times(self, start: datetime, end: datetime) -> list[datetime]:
        """Waktu bayar tiap order lunas. Dikelompokkan per jam di service (zona WIB),
        supaya sama di SQLite (test) dan PostgreSQL."""
        stmt = (
            select(Payment.paid_at)
            .join(Order, Order.id == Payment.order_id)
            .where(
                Payment.status == PaymentStatus.PAID.value,
                Payment.paid_at >= start,
                Payment.paid_at < end,
                Order.status != OrderStatus.CANCELLED.value,
            )
        )
        return list(self.db.scalars(stmt))
