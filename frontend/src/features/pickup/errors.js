// Pesan sesuai wireframes.md #21 (token tidak valid) dan #22 (sudah diambil).
export function describePickupError(err) {
  switch (err?.code) {
    case "PICKUP_NOT_FOUND":
      return {
        title: "Pickup tidak valid",
        message: "Token pickup tidak valid. Periksa kembali QR atau token customer.",
      };
    case "PICKUP_ALREADY_COMPLETED":
      return {
        title: "Pickup selesai",
        message: "Pesanan ini sudah diambil. Pickup kedua tidak dapat dilakukan.",
      };
    case "PICKUP_INVALID_STATE":
      return { title: "Pickup belum bisa", message: "Status order tidak mengizinkan pickup." };
    case "PICKUP_NOT_VERIFIED":
      return { title: "Belum diverifikasi", message: "Scan QR customer dulu sebelum menyelesaikan pickup." };
    default:
  }
  if (err?.status === 403) {
    return { title: "Tidak diizinkan", message: "Akunmu tidak boleh melakukan ini." };
  }
  return {
    title: "Belum bisa diproses",
    message: "Koneksi atau server bermasalah. Periksa daftar pickup dulu sebelum mencoba lagi.",
  };
}
