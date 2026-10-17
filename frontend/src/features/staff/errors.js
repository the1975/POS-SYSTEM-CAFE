// Pesan login: jelas tapi tidak membocorkan apakah emailnya terdaftar.
export function describeLoginError(err) {
  const status = err?.status;
  if (status === 401 || status === 403) return "Email atau kata sandi salah.";
  if (status === 422) return "Isi email dan kata sandi dengan benar.";
  if (status === 429) return "Terlalu banyak percobaan. Tunggu sebentar, lalu coba lagi.";
  if (typeof status === "number" && status >= 500) {
    return "Server sedang bermasalah. Coba lagi sebentar lagi.";
  }
  return "Tidak bisa terhubung. Periksa koneksi internet, lalu coba lagi.";
}
