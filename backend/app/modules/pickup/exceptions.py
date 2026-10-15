from app.core.exceptions import ConflictError, NotFoundError


class PickupNotFoundError(NotFoundError):
    # Dipakai juga untuk token salah: jangan membocorkan token mana yang ada.
    code = "PICKUP_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Data pickup tidak ditemukan.")


class PickupAlreadyCompletedError(ConflictError):
    code = "PICKUP_ALREADY_COMPLETED"

    def __init__(self) -> None:
        super().__init__("Pesanan ini sudah diambil.")


class PickupNotVerifiedError(ConflictError):
    code = "PICKUP_NOT_VERIFIED"

    def __init__(self) -> None:
        super().__init__("Token pickup belum diverifikasi.")


class PickupInvalidStateError(ConflictError):
    code = "PICKUP_INVALID_STATE"

    def __init__(self) -> None:
        super().__init__("Status order tidak mengizinkan pickup.")
