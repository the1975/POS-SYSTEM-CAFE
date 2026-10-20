// Bahasa status untuk staf (beda dengan bahasa customer di features/orders/statusLabels.js).
export const ORDER_STATUS_LABELS = {
  PENDING: "Menunggu bayar",
  CONFIRMED: "Dibayar",
  PREPARING: "Dimasak",
  READY: "Siap diambil",
  OVERDUE: "Terlambat diambil",
  COMPLETED: "Selesai",
  CANCELLED: "Dibatalkan",
};

export const PAYMENT_STATUS_LABELS = {
  PENDING: "Menunggu",
  WAITING_CASH: "Menunggu tunai",
  PAID: "Lunas",
  FAILED: "Gagal",
  REFUND_REQUESTED: "Refund diminta",
  REFUND_PENDING: "Refund diproses",
  REFUNDED: "Direfund",
  REFUND_FAILED: "Refund gagal",
};

export const orderStatusLabel = (s) => ORDER_STATUS_LABELS[s] ?? s;
export const paymentStatusLabel = (s) => (s ? PAYMENT_STATUS_LABELS[s] ?? s : "Belum ada pembayaran");

const toOptions = (labels, all) => [
  { value: "", label: all },
  ...Object.entries(labels).map(([value, label]) => ({ value, label })),
];
export const STATUS_FILTERS = toOptions(ORDER_STATUS_LABELS, "Semua status order");
export const PAYMENT_FILTERS = toOptions(PAYMENT_STATUS_LABELS, "Semua status bayar");

// Menu admin. Yang belum punya backend tampil sebagai "segera".
export const ADMIN_TABS = [
  { id: "orders", label: "Order", ready: true },
  { id: "dashboard", label: "Dashboard", ready: true },
  { id: "products", label: "Produk", ready: true },
  { id: "inventory", label: "Stok", ready: true },
  { id: "users", label: "Pengguna", ready: true },
];

// Sama dengan aturan backend (payments/refund.py): tunai, sudah lunas, order belum dimasak.
// Frontend hanya menyembunyikan tombol; backend tetap yang memutuskan.
export const canRefund = (o) =>
  Boolean(o.payment_id) &&
  o.payment_method === "CASH" &&
  o.payment_status === "PAID" &&
  o.status === "CONFIRMED";

export function pageInfo(p, noun = "order") {
  if (!p || p.total === 0) return { hasPrev: false, hasNext: false, label: "" };
  return {
    hasPrev: p.page > 1,
    hasNext: p.page < p.total_pages,
    label: `Halaman ${p.page} dari ${p.total_pages} · ${p.total} ${noun}`,
  };
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];

// "2026-10-18T14:05" -> "18 Okt 14.05" (jam setempat; manual supaya sama di semua perangkat).
export function formatShortDateTime(iso) {
  const d = new Date(iso ?? "");
  if (Number.isNaN(d.getTime())) return "—";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getDate()} ${MONTHS[d.getMonth()]} ${pad(d.getHours())}.${pad(d.getMinutes())}`;
}

export const MIN_REASON_LENGTH = 3;
export const isReasonValid = (text) => String(text ?? "").trim().length >= MIN_REASON_LENGTH;
