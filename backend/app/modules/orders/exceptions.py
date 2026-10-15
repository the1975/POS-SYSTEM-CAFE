from typing import Any

from app.core.exceptions import AppError, ConflictError, NotFoundError


class OrderNotFoundError(NotFoundError):
    # Dipakai juga untuk token salah/tidak ada: jangan membocorkan apakah order itu ada.
    code = "ORDER_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Order tidak ditemukan.")


class InvalidOrderItemsError(AppError):
    status_code = 422
    code = "INVALID_ORDER_ITEMS"

    def __init__(self, details: Any) -> None:
        super().__init__("Sebagian menu tidak bisa dipesan.", details)


class IdempotencyKeyReusedError(ConflictError):
    code = "IDEMPOTENCY_KEY_REUSED"

    def __init__(self) -> None:
        super().__init__("Kunci permintaan ini sudah dipakai untuk pesanan yang berbeda.")


class OrderNotCancellableError(ConflictError):
    code = "ORDER_NOT_CANCELLABLE"

    def __init__(self) -> None:
        super().__init__("Order ini sudah tidak bisa dibatalkan sendiri. Silakan hubungi kasir.")
