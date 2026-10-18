export const ACTIVE_STATUSES = ["CONFIRMED", "PREPARING"];
export const LATE_MINUTES = 15;

// Alasan remake yang diterima backend (remake_schema.py).
export const REMAKE_REASONS = [
  { value: "WRONG_MENU", label: "Salah menu" },
  { value: "WRONG_SIZE", label: "Salah ukuran" },
  { value: "WRONG_TOPPING", label: "Salah topping" },
  { value: "WRONG_QUANTITY", label: "Jumlah salah" },
  { value: "DAMAGED", label: "Rusak" },
  { value: "SPILLED", label: "Tumpah" },
  { value: "CUSTOMER_REQUEST", label: "Permintaan customer" },
  { value: "OTHER", label: "Lainnya" },
];

export function splitQueue(orders) {
  return {
    cooking: orders.filter((o) => o.status === "PREPARING"),
    waiting: orders.filter((o) => o.status === "CONFIRMED"),
  };
}

// Ganti order dengan versi terbaru dari server. Order yang tidak aktif lagi (mis. sudah
// READY) keluar dari antrean.
export function mergeOrder(orders, updated) {
  if (!ACTIVE_STATUSES.includes(updated.status)) {
    return orders.filter((o) => o.order_id !== updated.order_id);
  }
  if (!orders.some((o) => o.order_id === updated.order_id)) return [...orders, updated];
  return orders.map((o) => (o.order_id === updated.order_id ? updated : o));
}

export function elapsedMinutes(iso, now = Date.now()) {
  const t = Date.parse(iso ?? "");
  if (Number.isNaN(t)) return null;
  return Math.max(0, Math.floor((now - t) / 60000));
}

export function formatElapsed(min) {
  if (min == null) return "—";
  if (min < 1) return "baru saja";
  if (min < 60) return `${min} mnt`;
  return `${Math.floor(min / 60)} j ${min % 60} mnt`;
}

const ITEM_LABELS = { PENDING: "Menunggu", PREPARING: "Dimasak", READY: "Siap", REMAKE: "Dibuat ulang" };
export const itemStatusLabel = (status) => ITEM_LABELS[status] ?? status;

// Sesuai aturan backend: siap untuk item yang sedang dimasak/dibuat ulang;
// remake untuk item yang sedang dimasak atau sudah siap (selama order masih PREPARING).
export const canMarkReady = (item) => item.status === "PREPARING" || item.status === "REMAKE";
export const canRemake = (item) => item.status === "PREPARING" || item.status === "READY";
