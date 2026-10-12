// Kunci idempotensi: unik per "percobaan checkout". Request ulang dengan isi yang sama
// memakai kunci yang sama, sehingga tidak pernah membuat pesanan ganda.
export function newIdempotencyKey() {
  const c = globalThis.crypto;
  if (c?.randomUUID) return c.randomUUID();
  return `k-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;
}
