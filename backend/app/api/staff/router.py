"""Kumpulan router khusus staff (wajib login). Tambah router staff lain di sini."""

from fastapi import APIRouter

from app.modules.payments.router import router as payments_router
from app.modules.users.router import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(payments_router)
