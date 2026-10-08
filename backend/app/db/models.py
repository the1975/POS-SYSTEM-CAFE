"""Import semua model di sini supaya terdaftar di Base.metadata (dipakai Alembic).
Tambahkan modul baru setiap kali ada model baru."""
from app.modules.products.model import Category, Product  # noqa: F401
from app.modules.users.model import Role, User  # noqa: F401
