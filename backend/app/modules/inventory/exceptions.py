from typing import Any

from app.core.exceptions import ConflictError


class InsufficientStockError(ConflictError):
    code = "INSUFFICIENT_STOCK"

    def __init__(self, details: Any) -> None:
        super().__init__("Stok tidak cukup untuk sebagian menu.", details)
