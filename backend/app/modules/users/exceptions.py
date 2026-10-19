from app.core.exceptions import AppError, ConflictError, NotFoundError


class InvalidCredentialsError(AppError):
    status_code = 401
    code = "INVALID_CREDENTIALS"

    def __init__(self) -> None:
        # Satu pesan untuk semua penyebab (email salah / password salah / akun nonaktif),
        # supaya penyerang tidak bisa menebak email mana yang terdaftar.
        super().__init__("Email atau password salah.")


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"

    def __init__(self) -> None:
        super().__init__("Silakan login terlebih dahulu.")


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"

    def __init__(self) -> None:
        super().__init__("Anda tidak punya akses ke fitur ini.")


class UserNotFoundError(NotFoundError):
    code = "USER_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Pengguna tidak ditemukan.")


class EmailAlreadyUsedError(ConflictError):
    code = "EMAIL_ALREADY_USED"

    def __init__(self) -> None:
        super().__init__("Email sudah dipakai akun lain.")


class RoleNotFoundError(AppError):
    status_code = 422
    code = "ROLE_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Role tidak dikenal.")


class CannotModifySelfError(ConflictError):
    code = "CANNOT_MODIFY_SELF"

    def __init__(self) -> None:
        super().__init__("Kamu tidak bisa menonaktifkan atau mengganti role akunmu sendiri.")


class LastAdminError(ConflictError):
    code = "LAST_ADMIN"

    def __init__(self) -> None:
        super().__init__("Harus tersisa minimal satu admin aktif.")
