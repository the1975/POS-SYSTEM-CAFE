from app.core.exceptions import AppError, NotFoundError


class ProductNotFoundError(NotFoundError):
    code = "PRODUCT_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Produk tidak ditemukan.")


class CategoryNotFoundError(NotFoundError):
    code = "CATEGORY_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Kategori tidak ditemukan.")


class InvalidCategoryError(AppError):
    """Kategori yang dipilih pada body request tidak ada (beda dengan 404 URL tidak ada)."""

    status_code = 422
    code = "INVALID_CATEGORY"

    def __init__(self) -> None:
        super().__init__("Kategori tidak dikenal.")
