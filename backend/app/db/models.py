"""Import semua model di sini supaya terdaftar di Base.metadata (dipakai Alembic).
Tambahkan modul baru setiap kali ada model baru."""
from app.modules.inventory.model import Inventory, StockMovement, StockReservation  # noqa: F401
from app.modules.orders.model import Order, OrderItem  # noqa: F401
from app.modules.orders.revision_model import OrderRevision, OrderRevisionItem  # noqa: F401
from app.modules.products.model import Category, Product  # noqa: F401
from app.modules.users.model import Role, User  # noqa: F401
