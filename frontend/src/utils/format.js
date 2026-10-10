// Format rupiah tanpa bergantung pada data locale browser: 25000 -> "Rp25.000".
// Sengaja manual supaya hasilnya sama di semua perangkat (termasuk HP lama).
export function formatRupiah(amount) {
  const rounded = Math.round(Number(amount) || 0);
  return "Rp" + String(rounded).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
