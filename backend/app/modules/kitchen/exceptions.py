from app.core.exceptions import ConflictError, NotFoundError


class OrderItemNotFoundError(NotFoundError):
    code = "ORDER_ITEM_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Item order tidak ditemukan.")


class KitchenInvalidStateError(ConflictError):
    code = "KITCHEN_INVALID_STATE"

    def __init__(self) -> None:
        super().__init__("Status order tidak mengizinkan aksi ini.")


class OrderNotPaidError(ConflictError):
    code = "ORDER_NOT_PAID"

    def __init__(self) -> None:
        super().__init__("Order belum dibayar.")
