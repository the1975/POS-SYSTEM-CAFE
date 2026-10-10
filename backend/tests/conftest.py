import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models  # noqa: F401  (mendaftarkan semua tabel)
from app.db.base import Base
from app.db.dependencies import get_db
from app.main import create_app
from app.modules.inventory.model import Inventory
from app.modules.products.model import Category, Product

# Test API menu memakai SQLite in-memory dengan tabel yang dibutuhkan saja (cepat, tanpa Neon).
# Perilaku khusus PostgreSQL (konkurensi, locking) diuji dengan Postgres asli di Phase 13.
MENU_TABLES = [Category.__table__, Product.__table__, Inventory.__table__]


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine, tables=MENU_TABLES)
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
        "drinks": drinks.id, "food": food.id, "secret": secret.id,
        "es_teh": es_teh.id, "kopi": kopi.id, "nasi": nasi.id,
        "jus": jus.id, "mie": mie.id, "rahasia": rahasia.id,
    }
