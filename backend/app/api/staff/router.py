"""Kumpulan router khusus staff (wajib login). Tambah router staff lain di sini."""

from fastapi import APIRouter

from app.modules.kitchen.router import router as kitchen_router
from app.modules.orders.staff_router import router as staff_orders_router
from app.modules.payments.router import router as payments_router
from app.modules.users.router import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(payments_router)
router.include_router(staff_orders_router)
router.include_router(kitchen_router)
