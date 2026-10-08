"""Import semua model di sini supaya terdaftar di Base.metadata (dipakai Alembic).
Tambahkan modul baru setiap kali ada model baru."""
from app.modules.audit.model import AuditLog  # noqa: F401
from app.modules.inventory.model import Inventory, StockMovement, StockReservation  # noqa: F401
from app.modules.kitchen.model import RemakeEvent  # noqa: F401
from app.modules.notifications.model import Notification  # noqa: F401
from app.modules.orders.history_model import OrderStatusHistory  # noqa: F401
from app.modules.orders.model import Order, OrderItem  # noqa: F401
from app.modules.orders.revision_model import OrderRevision, OrderRevisionItem  # noqa: F401
from app.modules.payments.model import Payment, PaymentEvent  # noqa: F401
from app.modules.pickup.model import Pickup  # noqa: F401
from app.modules.products.model import Category, Product  # noqa: F401
from app.modules.users.model import Role, User  # noqa: F401
