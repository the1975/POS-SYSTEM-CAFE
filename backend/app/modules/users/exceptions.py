from app.core.exceptions import AppError


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
