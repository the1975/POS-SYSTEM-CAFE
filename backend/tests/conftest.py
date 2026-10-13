import os

# Harus di paling atas: diisi SEBELUM app di-import, karena get_settings() membaca env saat pertama dipanggil.
os.environ.setdefault("TRACKING_TOKEN_SECRET", "rahasia-khusus-test-jangan-dipakai-di-produksi")
os.environ.setdefault("TAX_RATE_PERCENT", "10")

import itertools
import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db import models  # noqa: F401  (mendaftarkan semua tabel)
from app.db.base import Base
from app.db.dependencies import get_db
from app.main import create_app
from app.modules.inventory.model import Inventory, StockMovement, StockReservation
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.service import InventoryService
from app.modules.orders.dependencies import get_order_service
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order, OrderItem
from app.modules.orders.repository import OrderRepository
from app.modules.orders.service import OrderService
from app.modules.products.model import Category, Product
from app.modules.users.model import Role, User

# Test API memakai SQLite in-memory dengan tabel yang dibutuhkan saja (cepat, tanpa Neon).
# Perilaku khusus PostgreSQL (SEQUENCE, konkurensi, locking) diuji dengan Postgres asli di Phase 13.
# Role & User ikut dibuat karena tabel lain punya foreign key ke sana (SQLite menolak insert
# kalau tabel induk FK tidak ada, begitu pemeriksaan foreign key dinyalakan).
TEST_TABLES = [
    Role.__table__,
    User.__table__,
    Category.__table__,
    Product.__table__,
    Inventory.__table__,
    Order.__table__,
    OrderItem.__table__,
    OrderStatusHistory.__table__,
    StockReservation.__table__,
    StockMovement.__table__,
]


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    # SQLite secara bawaan TIDAK memeriksa foreign key, padahal PostgreSQL memeriksanya.
    # Dinyalakan supaya bug urutan penyimpanan tertangkap di test, bukan di database asli.
    @event.listens_for(engine, "connect")
    def _enforce_foreign_keys(dbapi_connection, _record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine, tables=TEST_TABLES)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db

    counter = itertools.count(1)

    class TestOrderRepository(OrderRepository):
        # SQLite tidak punya SEQUENCE; di test, nomor urut dihitung manual.
        def next_order_sequence(self) -> int:
            return next(counter)

    def _order_service() -> OrderService:
        s = get_settings()
        return OrderService(
            TestOrderRepository(db),
            InventoryService(
                InventoryRepository(db),
                reservation_timeout_minutes=s.reservation_timeout_minutes,
            ),
            tax_rate_percent=s.tax_rate_percent,
            max_quantity_per_item=s.max_quantity_per_item,
        )

    app.dependency_overrides[get_order_service] = _order_service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def menu(db) -> dict[str, uuid.UUID]:
    """Data uji: 2 kategori aktif, 1 nonaktif; produk tampil, habis, tersembunyi."""
    drinks = Category(name="Minuman", sort_order=0)
    food = Category(name="Makanan", sort_order=1)
    secret = Category(name="Rahasia", sort_order=2, is_active=False)
    db.add_all([drinks, food, secret])
    db.flush()

    def product(cat, name, price, stock=None, available=True):
        p = Product(
            category_id=cat.id,
            name=name,
            price=Decimal(price),
            cost_price=Decimal(1000),
            is_available=available,
        )
        db.add(p)
        db.flush()
        if stock is not None:
            db.add(Inventory(product_id=p.id, quantity_available=stock))
        return p

    es_teh = product(drinks, "Es Teh", 8000, stock=10)
    kopi = product(drinks, "Kopi Susu", 18000, stock=0)  # habis
    nasi = product(food, "Nasi Goreng", 25000, stock=5)
    jus = product(food, "Jus 100% Jeruk", 15000)  # tanpa record inventory
    mie = product(food, "Mie Goreng", 22000, stock=5, available=False)  # disembunyikan
    rahasia = product(secret, "Menu Rahasia", 99000, stock=5)  # kategori nonaktif
    db.commit()
    return {
        "drinks": drinks.id,
        "food": food.id,
        "secret": secret.id,
        "es_teh": es_teh.id,
        "kopi": kopi.id,
        "nasi": nasi.id,
        "jus": jus.id,
        "mie": mie.id,
        "rahasia": rahasia.id,
    }
