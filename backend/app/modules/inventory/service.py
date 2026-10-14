"""Aturan bisnis stok: reservasi saat checkout. (Konversi saat dibayar, pelepasan saat
kedaluwarsa/batal menyusul di tahap berikutnya.)

Semua operasi berjalan di transaksi milik pemanggil (OrderService), jadi pengurangan stok,
baris order, reservasi, dan movement sukses atau gagal SEBAGAI SATU KESATUAN."""

import uuid
from datetime import UTC, datetime, timedelta

from app.modules.inventory.exceptions import InsufficientStockError, ReservationNotActiveError
from app.modules.inventory.model import (
    ReservationStatus,
    StockMovement,
    StockMovementType,
    StockReservation,
)
from app.modules.inventory.repository import InventoryRepository


class InventoryService:
    def __init__(self, repo: InventoryRepository, *, reservation_timeout_minutes: int) -> None:
        self.repo = repo
        self.reservation_timeout_minutes = reservation_timeout_minutes

    def reserve_stock(self, lines: dict[uuid.UUID, int], names: dict[uuid.UUID, str]) -> None:
        """Tahan stok semua item sekaligus; jika ada yang kurang, batalkan SEMUANYA."""
        shortages: list[uuid.UUID] = []
        # Urutan tetap (by id): dua order yang memesan produk sama tidak saling mengunci silang
        # (menghindari deadlock di database).
        for product_id in sorted(lines, key=str):
            if not self.repo.try_reserve(product_id, lines[product_id]):
                shortages.append(product_id)
        if shortages:
            self.repo.rollback()  # kembalikan pengurangan stok item lain di order yang sama
            available = self.repo.available_quantities(shortages)
            raise InsufficientStockError(
                [
                    {
                        "product_id": str(pid),
                        "name": names[pid],
                        "requested": lines[pid],
                        "available": available.get(pid, 0),  # tanpa record inventory = 0
                    }
                    for pid in shortages
                ]
            )

    def record_reservations(self, order_id: uuid.UUID, lines: dict[uuid.UUID, int]) -> None:
        """Catat reservasi + movement. Dipanggil SETELAH baris order ada (foreign key)."""
        expires_at = datetime.now(UTC) + timedelta(minutes=self.reservation_timeout_minutes)
        rows = []
        for product_id, quantity in lines.items():
            rows.append(
                StockReservation(
                    order_id=order_id,
                    product_id=product_id,
                    quantity=quantity,
                    status=ReservationStatus.ACTIVE.value,
                    expires_at=expires_at,
                )
            )
            # quantity di sini relatif terhadap quantity_available (turun karena ditahan).
            rows.append(
                StockMovement(
                    product_id=product_id,
                    movement_type=StockMovementType.RESERVATION.value,
                    quantity=-quantity,
                    reference_type="order",
                    reference_id=order_id,
                    reason="Stok ditahan saat checkout",
                )
            )
        self.repo.add(*rows)

    def convert_reservations(self, order_id: uuid.UUID, *, created_by: uuid.UUID | None) -> None:
        """Order dibayar: stok yang ditahan menjadi terjual (reserved turun + movement SALE).
        Berjalan di transaksi milik pemanggil."""
        reservations = self.repo.active_reservations(order_id)
        if not reservations:
            raise ReservationNotActiveError
        # Urutan tetap (by id), sama seperti reserve_stock, supaya tidak deadlock.
        for r in sorted(reservations, key=lambda r: str(r.product_id)):
            if not self.repo.consume_reserved(r.product_id, r.quantity):
                raise RuntimeError(f"Stok ditahan tidak konsisten untuk produk {r.product_id}")
        if self.repo.mark_reservations_converted(order_id) != len(reservations):
            raise ReservationNotActiveError  # berubah di tengah jalan (mis. baru kedaluwarsa)
        self.repo.add(
            *[
                StockMovement(
                    product_id=r.product_id,
                    movement_type=StockMovementType.SALE.value,
                    quantity=-r.quantity,
                    reference_type="order",
                    reference_id=order_id,
                    reason="Stok ditahan menjadi penjualan (pembayaran lunas)",
                    created_by=created_by,
                )
                for r in reservations
            ]
        )
