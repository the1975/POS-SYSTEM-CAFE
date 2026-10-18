// READY = siap diambil. OVERDUE = terlambat diambil, BUKAN batal: tetap boleh diambil.
export const PICKUP_STATUSES = ["READY", "OVERDUE"];

// Token dari backend: huruf/angka/-/_ sepanjang 8-200 (sama dengan validasi API).
const TOKEN_RE = /^[A-Za-z0-9_-]{8,200}$/;
export const cleanToken = (text) => String(text ?? "").trim();
export const isPlausibleToken = (text) => TOKEN_RE.test(cleanToken(text));

export const itemCount = (items) => (items ?? []).reduce((n, i) => n + i.quantity, 0);

// Yang paling lama siap, paling atas.
export function sortByReadyAt(orders) {
  const t = (o) => {
    const v = Date.parse(o.ready_at ?? "");
    return Number.isNaN(v) ? Infinity : v;
  };
  return [...orders].sort((a, b) => (t(a) < t(b) ? -1 : t(a) > t(b) ? 1 : 0));
}

// Order yang sudah diverifikasi (dari daftar) ditampilkan di panel yang sama dengan hasil scan.
export const orderFromRow = (row) => ({
  pickup_id: row.pickup_id,
  order_number: row.order_number,
  customer_name: row.customer_name,
  status: row.status,
  payment_status: null,
  items: row.items,
});
