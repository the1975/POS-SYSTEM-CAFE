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

// ---- Dapur ----
export function listKitchenOrders(token, { signal } = {}) {
  return apiFetch("/kitchen/orders?page=1&page_size=100", { headers: authHeader(token), signal });
}

export function startOrder(token, orderId) {
  return apiFetch(`/kitchen/orders/${orderId}/start`, { method: "POST", headers: authHeader(token) });
}

export function markItemReady(token, itemId) {
  return apiFetch(`/kitchen/order-items/${itemId}/ready`, {
    method: "POST",
    headers: authHeader(token),
  });
}

// notes opsional: kosong tidak dikirim.
export function remakeItem(token, itemId, { reason, notes }) {
  return apiFetch(`/kitchen/order-items/${itemId}/remake`, {
    method: "POST",
    headers: authHeader(token),
    body: JSON.stringify({ reason, notes: notes?.trim() || undefined }),
  });
}

// ---- Pickup ----
export function listPickupOrders(token, status, { signal } = {}) {
  const qs = new URLSearchParams({ status, page: "1", page_size: "100" });
  return apiFetch(`/pickup/orders?${qs}`, { headers: authHeader(token), signal });
}

export function verifyPickup(token, pickupToken) {
  return apiFetch("/pickup/verify", {
    method: "POST",
    headers: authHeader(token),
    body: JSON.stringify({ pickup_token: pickupToken }),
  });
}

export function completePickup(token, pickupId) {
  return apiFetch(`/pickup/${pickupId}/complete`, { method: "POST", headers: authHeader(token) });
}
