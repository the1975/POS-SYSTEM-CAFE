// Bahasa status untuk customer. Semua status resmi didefinisikan dari sekarang.
export const STATUS_LABELS = {
  PENDING: "Menunggu pembayaran",
  CONFIRMED: "Pesanan diterima",
  PREPARING: "Sedang disiapkan",
  READY: "Siap diambil",
  COMPLETED: "Selesai",
  CANCELLED: "Dibatalkan",
  OVERDUE: "Menunggu diambil",
};

export const statusLabel = (status) => STATUS_LABELS[status] ?? status;
