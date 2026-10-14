from app.core.responses import Pagination, build_pagination
from app.modules.orders.model import OrderStatus
from app.modules.orders.staff_repository import StaffOrderRepository
from app.modules.orders.staff_schema import StaffOrderOut
from app.modules.payments.model import PaymentStatus


class StaffOrderService:
    def __init__(self, repo: StaffOrderRepository) -> None:
        self.repo = repo

    def list_orders(
        self,
        *,
        status: OrderStatus | None,
        payment_status: PaymentStatus | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[StaffOrderOut], Pagination]:
        rows, total = self.repo.search(
            status=status,
            payment_status=payment_status,
            search=search,
            page=page,
            page_size=page_size,
        )
        items = [
            StaffOrderOut(
                order_id=order.id,
                order_number=order.order_number,
                customer_name=order.customer_name,
                status=order.status,
                payment_id=payment.id if payment else None,
                payment_method=order.payment_method,
                payment_status=payment.status if payment else None,
                total=order.total,
                created_at=order.created_at,
            )
            for order, payment in rows
        ]
        return items, build_pagination(page, page_size, total)
