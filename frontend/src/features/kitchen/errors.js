const BY_CODE = {
  KITCHEN_INVALID_STATE: "Status order sudah berubah. Antrean dimuat ulang.",
  ORDER_NOT_PAID: "Order ini belum dibayar, belum bisa dimasak.",
  REMAKE_ALREADY_IN_PROGRESS: "Item ini sudah dalam proses remake.",
  ORDER_ITEM_NOT_FOUND: "Item tidak ditemukan. Antrean dimuat ulang.",
  ORDER_NOT_FOUND: "Order tidak ditemukan. Antrean dimuat ulang.",
};

// Saat koneksi/server gagal, hasilnya tidak pasti: suruh cek antrean dulu.
export function describeKitchenError(err) {
  if (err?.status === 403) return "Akunmu tidak boleh melakukan ini.";
  if (err?.code && BY_CODE[err.code]) return BY_CODE[err.code];
  if (typeof err?.status === "number" && err.status >= 500) {
    return "Server sedang bermasalah. Periksa antrean dulu sebelum mencoba lagi.";
  }
  return "Koneksi bermasalah. Periksa antrean dulu sebelum mencoba lagi.";
}
