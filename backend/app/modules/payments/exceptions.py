from typing import Any

from app.core.exceptions import AppError, ConflictError, NotFoundError


class PaymentNotFoundError(NotFoundError):
    code = "PAYMENT_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Pembayaran tidak ditemukan.")


class PaymentAlreadyPaidError(ConflictError):
    code = "PAYMENT_ALREADY_PAID"

    def __init__(self) -> None:
        super().__init__("Pembayaran ini sudah lunas.")


class PaymentNotCashError(ConflictError):
    code = "PAYMENT_NOT_CASH"

    def __init__(self) -> None:
        super().__init__("Pembayaran ini bukan pembayaran tunai.")


class PaymentInvalidStateError(ConflictError):
    code = "PAYMENT_INVALID_STATE"

    def __init__(self) -> None:
        super().__init__("Pembayaran atau order tidak dalam status yang bisa dikonfirmasi.")


class InsufficientCashError(AppError):
    status_code = 422
    code = "INSUFFICIENT_CASH"

    def __init__(self, details: Any) -> None:
        super().__init__("Jumlah uang tidak mencukupi.", details)


class PaymentNotQrisError(ConflictError):
    code = "PAYMENT_NOT_QRIS"

    def __init__(self) -> None:
        super().__init__("Pembayaran order ini bukan QRIS.")


class PaymentExpiredError(ConflictError):
    code = "PAYMENT_EXPIRED"

    def __init__(self) -> None:
        super().__init__("Batas waktu pembayaran sudah lewat.")


class InvalidWebhookSignatureError(AppError):
    status_code = 401
    code = "INVALID_SIGNATURE"

    def __init__(self) -> None:
        super().__init__("Tanda tangan webhook tidak valid.")


class InvalidWebhookPayloadError(AppError):
    status_code = 400
    code = "INVALID_WEBHOOK_PAYLOAD"

    def __init__(self) -> None:
        super().__init__("Isi webhook tidak valid.")


class PaymentAmountMismatchError(ConflictError):
    code = "PAYMENT_AMOUNT_MISMATCH"

    def __init__(self, details: Any) -> None:
        super().__init__("Jumlah pembayaran tidak sama dengan tagihan.", details)
