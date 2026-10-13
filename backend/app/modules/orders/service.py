"""Aturan bisnis pembuatan & pembacaan order (sisi customer guest)."""
import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.core.security import derive_tracking_token, hash_token, verify_token
from app.modules.inventory.service import InventoryService
from app.modules.orders.exceptions import (
    IdempotencyKeyReusedError,
    InvalidOrderItemsError,
    OrderNotFoundError,
)
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order, OrderItem, OrderItemStatus, OrderStatus
from app.modules.orders.order_number import format_order_number
from app.modules.orders.pricing import calculate_totals
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schema import (
    CreateOrderIn,
    OrderCreatedOut,
    OrderDetailOut,
    OrderItemOut,
)
from app.modules.products.model import Product


class OrderService:
    def __init__(
        self,
        repo: OrderRepository,
        inventory: InventoryService,
        *,
        tax_rate_percent: Decimal,
        max_quantity_per_item: int,
    ) -> None:
        self.repo = repo
        self.inventory = inventory
        self.tax_rate_percent = tax_rate_percent
        self.max_quantity_per_item = max_quantity_per_item

    # ---- buat order ------------------------------------------------------------------
    def create_order(
        self, data: CreateOrderIn, idempotency_key: str
    ) -> tuple[OrderCreatedOut, bool]:
        """Mengembalikan (order, replayed). replayed=True bila kunci yang sama sudah pernah dipakai."""
        lines = self._merge_lines(data)

        existing = self.repo.find_by_idempotency_key(idempotency_key)
        if existing is not None:
            return self._replay(existing, data, lines), True

        products = self._load_orderable(lines)  # 422 bila ada menu yang tidak bisa dipesan
        try:
            # Urutan penting: stok ditahan DULU (atomik). Bila stok kurang, tidak ada nomor
            # order yang terpakai dan tidak ada baris yang tersimpan.
            self.inventory.reserve_stock(lines, {pid: p.name for pid, p in products.items()})
            order, history = self._build_order(data, lines, products, idempotency_key)
            self.repo.add(order, history)
            self.inventory.record_reservations(order.id, lines)
            self.repo.commit()  # stok + order + item + riwayat + reservasi: semua atau tidak sama sekali
        except IntegrityError:
            # Dua request dengan kunci sama masuk bersamaan: yang kalah balapan menerima
            # order milik yang menang. Rollback juga melepas stok yang sempat ditahan.
            self.repo.rollback()
            existing = self.repo.find_by_idempotency_key(idempotency_key)
            if existing is None:
                raise
            return self._replay(existing, data, lines), True
        return self._created_out(order), False

    @staticmethod
    def _merge_lines(data: CreateOrderIn) -> dict[uuid.UUID, int]:
        """Baris produk yang sama digabung (jumlahnya dijumlahkan)."""
        lines: dict[uuid.UUID, int] = {}
        for item in data.items:
            lines[item.product_id] = lines.get(item.product_id, 0) + item.quantity
        return lines

    def _load_orderable(self, lines: dict[uuid.UUID, int]) -> dict[uuid.UUID, Product]:
        products = self.repo.get_orderable_products(list(lines))
        problems = []
        for product_id, quantity in lines.items():
            if product_id not in products:
                # Satu alasan untuk "tidak ada" maupun "tidak tersedia": tidak membocorkan detail.
                problems.append({"product_id": str(product_id), "reason": "NOT_AVAILABLE"})
            elif quantity > self.max_quantity_per_item:
                problems.append(
                    {
                        "product_id": str(product_id),
                        "reason": "QUANTITY_EXCEEDS_LIMIT",
                        "max_quantity": self.max_quantity_per_item,
                    }
                )
        if problems:
            raise InvalidOrderItemsError(problems)
        return products

    def _build_order(
        self,
        data: CreateOrderIn,
        lines: dict[uuid.UUID, int],
        products: dict[uuid.UUID, Product],
        idempotency_key: str,
    ) -> tuple[Order, OrderStatusHistory]:
        order_id = uuid.uuid4()
        items: list[OrderItem] = []
        subtotal = Decimal(0)
        for product_id, quantity in lines.items():
            product = products[product_id]
            line_total = product.price * quantity  # harga dari DATABASE, bukan dari client
            subtotal += line_total
            items.append(
                OrderItem(
                    product_id=product.id,
                    # Snapshot: histori tetap benar walau nama/harga produk berubah kemudian.
                    product_name_snapshot=product.name,
                    unit_price=product.price,
                    quantity=quantity,
                    subtotal=line_total,
                    status=OrderItemStatus.PENDING.value,
                )
            )
        totals = calculate_totals(subtotal, Decimal(0), self.tax_rate_percent)

        order = Order(
            id=order_id,
            order_number=format_order_number(self.repo.next_order_sequence()),
            customer_name=data.customer_name,
            idempotency_key=idempotency_key,
            tracking_token_hash=hash_token(derive_tracking_token(order_id)),
            status=OrderStatus.PENDING.value,
            subtotal=totals.subtotal,
            discount_amount=totals.discount_amount,
            tax_amount=totals.tax_amount,
            total=totals.total,
            payment_method=data.payment_method.value,
            items=items,
        )
        history = OrderStatusHistory(
            order_id=order_id,
            from_status=None,
            to_status=OrderStatus.PENDING.value,
            changed_by=None,  # dibuat oleh customer guest
            reason="Order dibuat",
        )
        return order, history

    def _replay(
        self, existing: Order, data: CreateOrderIn, lines: dict[uuid.UUID, int]
    ) -> OrderCreatedOut:
        stored = {item.product_id: item.quantity for item in existing.items}
        same_request = (
            stored == lines
            and existing.customer_name == data.customer_name
            and existing.payment_method == data.payment_method.value
        )
        if not same_request:
            raise IdempotencyKeyReusedError
        return self._created_out(existing)

    @staticmethod
    def _created_out(order: Order) -> OrderCreatedOut:
        return OrderCreatedOut(
            order_id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            status=order.status,
            payment_method=order.payment_method,
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            tax_amount=order.tax_amount,
            total=order.total,
            tracking_token=derive_tracking_token(order.id),
        )

    # ---- baca order (customer dengan tracking token) -------------------------------------
    def get_order_for_customer(self, order_id: uuid.UUID, token: str | None) -> OrderDetailOut:
        order = self.repo.get_by_id(order_id)
        # Token kosong, salah, atau order tidak ada: semuanya 404 yang sama.
        if order is None or not token or not verify_token(token, order.tracking_token_hash):
            raise OrderNotFoundError
        return OrderDetailOut(
            order_id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            status=order.status,
            payment_method=order.payment_method,
            items=[
                OrderItemOut(name=i.product_name_snapshot, quantity=i.quantity, status=i.status)
                for i in order.items
            ],
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            tax_amount=order.tax_amount,
            total=order.total,
        )
