"""Kumpulan router yang boleh diakses customer guest. Tambah router customer lain di sini."""

from fastapi import APIRouter

from app.modules.orders.router import router as orders_router
from app.modules.payments.customer_router import router as payments_customer_router
from app.modules.products.router import router as menu_router

router = APIRouter()
router.include_router(menu_router)
router.include_router(orders_router)
router.include_router(payments_customer_router)
