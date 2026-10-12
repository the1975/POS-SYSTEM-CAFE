// Menyimpan token tracking di perangkat customer supaya halaman pesanan bisa dibuka lagi.
// Token hanya ada di sini (server hanya menyimpan hash-nya). Dibatasi 10 pesanan terakhir.
export const ORDERS_KEY = "monster-cafe:orders:v1";
export const MAX_SAVED_ORDERS = 10;

export function parseOrderAccess(raw) {
  try {
    const list = JSON.parse(raw);
    if (!Array.isArray(list)) return [];
    return list.filter(
      (o) =>
        o &&
        typeof o.orderId === "string" && o.orderId &&
        typeof o.orderNumber === "string" && o.orderNumber &&
        typeof o.token === "string" && o.token
    ).map((o) => ({ orderId: o.orderId, orderNumber: o.orderNumber, token: o.token }));
  } catch {
    return [];
  }
}

export function addOrderAccess(list, entry, max = MAX_SAVED_ORDERS) {
  const rest = list.filter((o) => o.orderId !== entry.orderId);
  return [entry, ...rest].slice(0, max); // yang terbaru di depan, yang lama dibuang
}

function read() {
  try {
    return parseOrderAccess(window.localStorage.getItem(ORDERS_KEY));
  } catch {
    return [];
  }
}

export function saveOrderAccess(entry) {
  try {
    window.localStorage.setItem(ORDERS_KEY, JSON.stringify(addOrderAccess(read(), entry)));
  } catch {
    /* penyimpanan diblokir: halaman konfirmasi tetap tampil sekali lewat state navigasi */
  }
}

export const getOrderAccess = (orderId) => read().find((o) => o.orderId === orderId) ?? null;
