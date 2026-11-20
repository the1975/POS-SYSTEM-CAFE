from decimal import Decimal

from sqlalchemy import select

from app.modules.orders.model import OrderItem
from app.modules.products.model import Product

API = "/api/v1"


def test_order_item_snapshots_unit_cost(client, menu, db):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu["es_teh"]), "quantity": 2}],
        "payment_method": "CASH",
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": "kunci-hpp-001"})
    assert r.status_code == 201

    product = db.get(Product, menu["es_teh"])
    product.cost_price = Decimal(5000)  # HPP berubah SETELAH order dibuat
    db.commit()

    item = db.scalars(select(OrderItem)).one()
    assert item.unit_cost == Decimal(1000)  # tetap HPP saat order dibuat
