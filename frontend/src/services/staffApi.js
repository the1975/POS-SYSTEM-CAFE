import { apiFetch } from "./api";

const authHeader = (token) => ({ Authorization: `Bearer ${token}` });

// Daftar order untuk staff. paymentStatus mis. "WAITING_CASH" = antrean kasir.
export function listStaffOrders(token, { paymentStatus, search, pageSize = 50, signal } = {}) {
  const qs = new URLSearchParams({ page: "1", page_size: String(pageSize) });
  if (paymentStatus) qs.set("payment_status", paymentStatus);
  if (search) qs.set("search", search);
  return apiFetch(`/staff/orders?${qs}`, { headers: authHeader(token), signal });
}

// Hanya uang yang diterima yang dikirim. Kembalian dihitung backend.
export function confirmCash(token, paymentId, cashReceived) {
  return apiFetch(`/payments/${paymentId}/cash-confirm`, {
    method: "POST",
    headers: authHeader(token),
    body: JSON.stringify({ cash_received: String(cashReceived) }),
  });
}
