const BY_CODE = {
  INSUFFICIENT_CASH: "Uang belum mencukupi.",
  PAYMENT_ALREADY_PAID: "Pembayaran ini sudah dikonfirmasi. Muat ulang antrean.",
  PAYMENT_INVALID_STATE:
    "Order ini tidak bisa dibayar lagi (mungkin sudah dibatalkan atau kedaluwarsa).",
  PAYMENT_NOT_FOUND: "Pembayaran tidak ditemukan. Muat ulang antrean.",
  PAYMENT_NOT_CASH: "Order ini bukan pembayaran tunai.",
};

// Saat koneksi/server gagal, hasilnya tidak pasti: suruh cek antrean, jangan klaim "belum tercatat".
export function describeCashError(err) {
  if (err?.status === 403) return "Akunmu tidak boleh mengonfirmasi pembayaran.";
  if (err?.code && BY_CODE[err.code]) return BY_CODE[err.code];
  if (typeof err?.status === "number" && err.status >= 500) {
    return "Server sedang bermasalah. Periksa antrean dulu sebelum mencoba lagi.";
  }
  return "Koneksi bermasalah. Periksa antrean dulu sebelum mencoba lagi.";
}
