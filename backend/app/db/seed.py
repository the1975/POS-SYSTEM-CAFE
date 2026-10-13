"""Seed data awal. Idempotent: aman dijalankan berulang (tidak membuat duplikat,
tidak menimpa password admin yang sudah ada).

    python -m app.db.seed          # 5 role + akun admin
    python -m app.db.seed --demo   # + kategori/produk/stok contoh (tidak jalan di production)
"""

import argparse
import sys
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db import models  # noqa: F401  (mendaftarkan semua tabel)
from app.db.session import get_session_factory
from app.modules.inventory.model import Inventory, StockMovement, StockMovementType
from app.modules.products.model import Category, Product
from app.modules.users.model import Role, RoleName, User

MIN_ADMIN_PASSWORD_LENGTH = 12

ROLE_DESCRIPTIONS = {
    RoleName.ADMIN: "Owner/admin: produk, inventory, user, laporan, konfigurasi",
    RoleName.CONTROLLER: "Order/shift controller: exception & monitoring operasional",
    RoleName.KITCHEN: "Dapur: antrean, status item, remake",
    RoleName.CASHIER: "Kasir: pembayaran cash, verifikasi order, cetak ulang",
    RoleName.PICKUP: "Pickup: verifikasi dan serah terima order",
}

# kategori -> [(nama, harga jual, HPP, stok awal)]
DEMO_MENU = {
    "Minuman": [("Es Teh", 8000, 2000, 50), ("Kopi Susu", 18000, 7000, 40)],
    "Makanan": [("Nasi Goreng", 25000, 11000, 30), ("Mie Goreng", 22000, 9000, 30)],
    "Camilan": [("Kentang Goreng", 15000, 6000, 40)],
}
DEMO_REORDER_LEVEL = 5


def seed_roles(db: Session) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for name in RoleName:
        role = db.scalar(select(Role).where(Role.name == name.value))
        if role is None:
            role = Role(name=name.value, description=ROLE_DESCRIPTIONS[name])
            db.add(role)
        roles[name.value] = role
    db.flush()  # isi id UUID
    return roles


def seed_admin(db: Session, roles: dict[str, Role]) -> str:
    settings = get_settings()
    email = settings.seed_admin_email
    password = settings.seed_admin_password
    if not email or password is None:
        return "dilewati (SEED_ADMIN_EMAIL / SEED_ADMIN_PASSWORD belum diisi di .env)"
    secret = password.get_secret_value()
    if len(secret) < MIN_ADMIN_PASSWORD_LENGTH:
        raise SystemExit(f"SEED_ADMIN_PASSWORD minimal {MIN_ADMIN_PASSWORD_LENGTH} karakter.")
    if db.scalar(select(User).where(User.email == email)) is not None:
        return "sudah ada (password tidak diubah)"
    db.add(
        User(
            role_id=roles[RoleName.ADMIN.value].id,
            name="Admin",
            email=email,
            password_hash=hash_password(secret),
        )
    )
    return "dibuat"


def seed_demo(db: Session) -> tuple[int, int]:
    new_categories = new_products = 0
    for order, (cat_name, items) in enumerate(DEMO_MENU.items()):
        category = db.scalar(select(Category).where(Category.name == cat_name))
        if category is None:
            category = Category(name=cat_name, sort_order=order)
            db.add(category)
            db.flush()
            new_categories += 1
        for name, price, cost, stock in items:
            product = db.scalar(
                select(Product).where(Product.category_id == category.id, Product.name == name)
            )
            if product is not None:
                continue
            product = Product(
                category_id=category.id,
                name=name,
                price=Decimal(price),
                cost_price=Decimal(cost),
            )
            db.add(product)
            db.flush()
            db.add(
                Inventory(
                    product_id=product.id,
                    quantity_available=stock,
                    reorder_level=DEMO_REORDER_LEVEL,
                )
            )
            # Setiap perubahan stok harus tercatat di stock_movements.
            db.add(
                StockMovement(
                    product_id=product.id,
                    movement_type=StockMovementType.RESTOCK.value,
                    quantity=stock,
                    reason="Seed stok awal (demo)",
                )
            )
            new_products += 1
    return new_categories, new_products


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--demo", action="store_true", help="tambah kategori/produk/stok contoh")
    args = parser.parse_args()

    if args.demo and get_settings().is_production:
        sys.exit("Data demo tidak boleh di-seed di production.")

    with get_session_factory()() as db, db.begin():
        roles = seed_roles(db)
        print(f"Role   : {len(roles)} tersedia")
        print(f"Admin  : {seed_admin(db, roles)}")
        if args.demo:
            categories, products = seed_demo(db)
            print(f"Demo   : +{categories} kategori, +{products} produk (beserta stok)")


if __name__ == "__main__":
    main()
