// Kelompokkan item per kunci (mis. nama kategori). Urutan kemunculan dipertahankan.
export function groupBy(items, keyOf) {
  const byKey = new Map();
  for (const it of items) {
    const key = keyOf(it) || "Lainnya";
    if (!byKey.has(key)) byKey.set(key, []);
    byKey.get(key).push(it);
  }
  return [...byKey.entries()].map(([label, list]) => ({ label, items: list }));
}
