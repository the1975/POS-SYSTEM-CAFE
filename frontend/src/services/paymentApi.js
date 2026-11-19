import { apiFetch } from "./api";

// Minta instruksi bayar QRIS. Aman dipanggil ulang: backend memakai transaksi yang sama.
export function createQris(orderId, token) {
  return apiFetch("/payments/qris", {
    method: "POST",
    headers: { "X-Tracking-Token": token },
    body: JSON.stringify({ order_id: orderId }),
  });
}
