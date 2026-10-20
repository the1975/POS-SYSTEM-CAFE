export const STOCK_PAGE_SIZE = 20;
export const MAX_QTY = 100000;
export const MIN_REASON = 3;
export const MAX_REASON = 500;

// Tiga jenis koreksi yang boleh dipilih admin (sama dengan backend: MANUAL_TYPES).
// sign: + menambah stok, - mengurangi.
export const STOCK_ACTIONS = [
  { id: "add", label: "Tambah stok", sign: 1, type: "RESTOCK", hint: "Barang masuk / restock." },
  { id: "reduce", label: "Koreksi kurang", sign: -1, type: "ADJUSTMENT", hint: "Hasil hitung ulang lebih sedikit." },
  { id: "waste", label: "Rusak / terbuang", sign: -1, type: "WASTE", hint: "Barang rusak, basi, atau tumpah." },
];

export const actionById = (id) => STOCK_ACTIONS.find((a) => a.id === id) ?? STOCK_ACTIONS[0];

// Jumlah: hanya angka bulat 1..100000. Selain itu belum valid (null).
export function parseQty(text) {
  const clean = String(text ?? "").trim();
  if (!/^\d{1,6}$/.test(clean)) return null;
  const n = Number(clean);
  return n >= 1 && n <= MAX_QTY ? n : null;
}

// Perubahan bertanda untuk dikirim ke backend (null kalau jumlah belum valid).
export function signedDelta(actionId, qtyText) {
  const qty = parseQty(qtyText);
  return qty === null ? null : actionById(actionId).sign * qty;
}

// Stok sesudah koreksi, untuk pratinjau "25 → 40". Null kalau jumlah belum valid.
export function stockAfter(current, actionId, qtyText) {
  const delta = signedDelta(actionId, qtyText);
  return delta === null ? null : current + delta;
}

// Valid kalau jumlah benar, alasan cukup, dan stok tidak jadi minus (backend juga menolaknya).
export function isAdjustValid(current, actionId, qtyText, reason) {
  const after = stockAfter(current, actionId, qtyText);
  const why = reason.trim();
  return after !== null && after >= 0 && why.length >= MIN_REASON && why.length <= MAX_REASON;
}

export function buildAdjustBody(actionId, qtyText, reason) {
  return {
    quantity: signedDelta(actionId, qtyText),
    reason: reason.trim(),
    movement_type: actionById(actionId).type,
  };
}

// Status stok untuk label di daftar.
export function stockLabel(item) {
  return item.quantity_available <= 0 ? "Habis" : null;
}

// Saat koneksi/server gagal hasilnya tidak pasti: cek angka stok di daftar dulu sebelum mengulang.
export function describeStockError(err) {
  switch (err?.code) {
    case "ADJUST_EXCEEDS_STOCK":
      return "Stok tidak cukup untuk dikurangi sebanyak itu. Muat ulang daftar untuk melihat stok terbaru.";
    case "PRODUCT_NOT_FOUND":
      return "Produk tidak ditemukan. Muat ulang daftar stok.";
    default:
  }
  if (err?.status === 403) return "Hanya admin yang boleh mengoreksi stok.";
  if (err?.status === 422) return "Periksa isian: jumlah berupa angka, alasan minimal 3 huruf.";
  return "Koneksi atau server bermasalah. Periksa angka stok di daftar dulu sebelum mencoba lagi.";
}
