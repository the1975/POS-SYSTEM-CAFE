import { formatRupiah } from "../../utils/format";

export const PRODUCTS_PAGE_SIZE = 20;
export const MAX_NAME_LENGTH = 150;

export const PRODUCT_STATUS_FILTERS = [
  { value: "", label: "Semua produk" },
  { value: "true", label: "Tampil di menu" },
  { value: "false", label: "Disembunyikan" },
];

// Isian uang: hanya angka bulat Rupiah ("25000"). Selain itu dianggap belum valid (null).
export function parseRupiah(text) {
  const clean = String(text ?? "").trim();
  return /^\d{1,10}$/.test(clean) ? Number(clean) : null;
}

// "= Rp25.000" di bawah kolom isian, supaya orang gaptek yakin angkanya benar.
export function moneyHint(text) {
  const n = parseRupiah(text);
  return n === null ? "" : `= ${formatRupiah(n)}`;
}

export const emptyProductForm = (categoryId = "") => ({
  name: "",
  categoryId,
  price: "",
  costPrice: "",
  description: "",
  imageUrl: "",
  isAvailable: true,
});

const money = (value) => String(Math.round(Number(value) || 0));

export function formFromProduct(p) {
  return {
    name: p.name,
    categoryId: p.category_id,
    price: money(p.price),
    costPrice: money(p.cost_price),
    description: p.description ?? "",
    imageUrl: p.image_url ?? "",
    isAvailable: p.is_available,
  };
}

// Aturan sama dengan backend (products/admin_schema.py).
export function isProductFormValid(form) {
  const name = form.name.trim();
  return (
    name.length > 0 &&
    name.length <= MAX_NAME_LENGTH &&
    Boolean(form.categoryId) &&
    parseRupiah(form.price) !== null &&
    parseRupiah(form.costPrice) !== null
  );
}

// Harga jual di bawah HPP = rugi. Hanya peringatan, bukan larangan.
export function isSellingAtLoss(form) {
  const price = parseRupiah(form.price);
  const cost = parseRupiah(form.costPrice);
  return price !== null && cost !== null && cost > price;
}

const orNull = (text) => String(text ?? "").trim() || null;

export function buildProductBody(form) {
  return {
    category_id: form.categoryId,
    name: form.name.trim(),
    description: orNull(form.description),
    price: parseRupiah(form.price),
    cost_price: parseRupiah(form.costPrice),
    image_url: orNull(form.imageUrl),
    is_available: form.isAvailable,
  };
}

// Hanya field yang berubah yang dikirim (backend menolak body kosong).
export function buildProductPatch(product, form) {
  const next = buildProductBody(form);
  const current = {
    category_id: product.category_id,
    name: product.name,
    description: product.description ?? null,
    price: Math.round(Number(product.price)),
    cost_price: Math.round(Number(product.cost_price)),
    image_url: product.image_url ?? null,
    is_available: product.is_available,
  };
  const patch = {};
  for (const key of Object.keys(next)) {
    if (next[key] !== current[key]) patch[key] = next[key];
  }
  return patch;
}

// Saat koneksi/server gagal hasilnya tidak pasti (produk bisa sudah tersimpan): cek daftar dulu.
export function describeProductError(err) {
  switch (err?.code) {
    case "INVALID_CATEGORY":
      return "Kategori tidak dikenal. Muat ulang halaman.";
    case "PRODUCT_NOT_FOUND":
      return "Produk tidak ditemukan. Muat ulang daftar produk.";
    default:
  }
  if (err?.status === 403) return "Hanya admin yang boleh mengelola produk.";
  if (err?.status === 422) return "Periksa isian: nama wajib, harga dan HPP berupa angka.";
  return "Koneksi atau server bermasalah. Periksa daftar produk dulu sebelum mencoba lagi.";
}
