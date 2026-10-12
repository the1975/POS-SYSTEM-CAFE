import { ApiError } from "../../services/api";

// Mengubah error API/jaringan menjadi pesan yang jelas: apa yang terjadi, apakah aman,
// dan apa yang bisa dilakukan (design-system.md §44).
export function describeCheckoutError(err, cartItems) {
  if (err instanceof ApiError) {
    if (err.status === 422 && err.code === "INVALID_ORDER_ITEMS") {
      const problems = Array.isArray(err.details) ? err.details : [];
      const byId = new Map(cartItems.map((i) => [i.productId, i]));
      const unavailable = problems
        .filter((p) => p.reason === "NOT_AVAILABLE")
        .map((p) => byId.get(p.product_id))
        .filter(Boolean);
      const overLimit = problems.filter((p) => p.reason === "QUANTITY_EXCEEDS_LIMIT");
      if (unavailable.length > 0) {
        return {
          kind: "unavailable",
          title: "Sebagian menu sudah tidak tersedia.",
          message: "Hapus menu berikut dari keranjang, lalu coba lagi.",
          unavailable,
        };
      }
      if (overLimit.length > 0) {
        return {
          kind: "limit",
          title: "Jumlah terlalu banyak.",
          message: `Maksimal ${overLimit[0].max_quantity} porsi per menu. Kurangi jumlahnya di keranjang.`,
        };
      }
    }
    if (err.status >= 500) {
      return {
        kind: "server",
        title: "Server sedang bermasalah.",
        message: "Pesananmu tidak akan terbuat dua kali. Coba lagi sebentar lagi.",
      };
    }
    return { kind: "other", title: "Pesanan belum bisa dibuat.", message: err.message };
  }
  // Bukan ApiError = permintaan tidak sampai (offline/putus).
  return {
    kind: "network",
    title: "Koneksi bermasalah.",
    message: "Periksa internet lalu coba lagi. Aman: pesananmu tidak akan terbuat dua kali.",
  };
}
