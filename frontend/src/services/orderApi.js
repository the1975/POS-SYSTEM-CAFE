import { apiFetch } from "./api";

// Hanya product_id & quantity yang dikirim. Harga/total TIDAK dikirim: backend yang menghitung.
export function createOrder({ customerName, paymentMethod, items }, idempotencyKey) {
  return apiFetch("/orders", {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify({
      customer_name: customerName,
      payment_method: paymentMethod,
      items,
    }),
  });
}

// Token tracking lewat header (bukan URL) agar tidak tersimpan di riwayat browser/log.
export function getOrder(orderId, token, { signal } = {}) {
  return apiFetch(`/orders/${orderId}`, { headers: { "X-Tracking-Token": token }, signal });
}

// Batalkan pesanan yang belum dibayar. Token lewat header, sama seperti getOrder.
export function cancelOrder(orderId, token) {
  return apiFetch(`/orders/${orderId}/cancel`, {
    method: "POST",
    headers: { "X-Tracking-Token": token },
  });
}
