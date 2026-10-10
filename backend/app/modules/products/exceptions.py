from app.core.exceptions import NotFoundError


class ProductNotFoundError(NotFoundError):
    code = "PRODUCT_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Produk tidak ditemukan.")


class CategoryNotFoundError(NotFoundError):
    code = "CATEGORY_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Kategori tidak ditemukan.")
