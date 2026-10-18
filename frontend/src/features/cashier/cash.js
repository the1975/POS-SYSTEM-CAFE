export const MAX_CASH_DIGITS = 9;

// "Rp100.000" atau "100000" -> 100000. Selain angka diabaikan; kosong -> 0.
export function parseRupiahInput(text) {
  const digits = String(text ?? "").replace(/\D/g, "").slice(0, MAX_CASH_DIGITS);
  return digits ? Number(digits) : 0;
}

export const changeFor = (total, received) => Math.max(0, Math.round(received - total));

// Tombol cepat: uang pas, lalu pecahan umum yang cukup untuk membayar.
export function quickAmounts(total) {
  const bills = [20000, 50000, 100000].filter((v) => v > total);
  return [Math.ceil(total), ...bills].slice(0, 4);
}
