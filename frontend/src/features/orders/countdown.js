// Hitung mundur batas bayar. Fungsi murni supaya mudah dites.

// Hanya pesanan yang belum dibayar yang boleh dibatalkan customer (aturan sama dengan backend).
export const canCancel = (order) => order?.status === "PENDING";

// Sisa detik sampai expiresAt (ISO). null bila tidak ada/tidak valid. Tidak pernah negatif.
export function secondsLeft(expiresAt, now = Date.now()) {
  if (!expiresAt) return null;
  const end = Date.parse(expiresAt);
  if (Number.isNaN(end)) return null;
  return Math.max(0, Math.ceil((end - now) / 1000));
}

// 402 detik -> "6:42"
export function formatCountdown(seconds) {
  const s = Math.max(0, Math.floor(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
