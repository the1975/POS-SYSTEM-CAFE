// Saat koneksi/server gagal hasilnya tidak pasti: suruh cek daftar dulu (mencegah refund ganda).
export function describeRefundError(err) {
  if (err?.status === 403) return "Hanya admin yang boleh melakukan refund.";
  if (err?.code === "REFUND_NOT_ALLOWED") {
    return err.message || "Refund tidak bisa dilakukan untuk order ini. Muat ulang daftar order.";
  }
  if (err?.code === "REFUND_AMOUNT_INVALID") return "Jumlah refund harus sama dengan total pembayaran.";
  if (err?.code === "PAYMENT_NOT_FOUND") return "Pembayaran tidak ditemukan. Muat ulang daftar order.";
  if (err?.status === 422) return "Isi alasan refund dengan jelas (minimal 3 karakter).";
  return "Koneksi atau server bermasalah. Periksa daftar order dulu sebelum mencoba lagi.";
}
