"""Kumpulan router khusus staff (wajib login). Tambah router staff lain di sini."""

from fastapi import APIRouter

from app.modules.analytics.router import router as analytics_router
from app.modules.kitchen.router import router as kitchen_router
from app.modules.orders.staff_router import router as staff_orders_router
from app.modules.payments.router import router as payments_router
from app.modules.pickup.router import router as pickup_router
from app.modules.products.admin_router import list_router as products_admin_list_router
from app.modules.products.admin_router import router as products_admin_router
from app.modules.users.admin_router import router as users_admin_router
from app.modules.users.router import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(payments_router)
router.include_router(staff_orders_router)
router.include_router(kitchen_router)
router.include_router(pickup_router)
router.include_router(users_admin_router)
router.include_router(products_admin_router)
router.include_router(products_admin_list_router)
router.include_router(analytics_router)
