import { useState } from "react";
import { createProduct, updateProduct } from "../../services/staffApi";
import { formatRupiah } from "../../utils/format";
import {
  MAX_NAME_LENGTH,
  buildProductBody,
  buildProductPatch,
  describeProductError,
  emptyProductForm,
  formFromProduct,
  isProductFormValid,
  isSellingAtLoss,
  moneyHint,
} from "./products";

// product = null -> mode Tambah; product berisi -> mode Ubah.
export default function ProductFormPanel({ token, product, categories, onBack, onDone, onUnauthorized }) {
  const isEdit = Boolean(product);
  const [form, setForm] = useState(() => (isEdit ? formFromProduct(product) : emptyProductForm()));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(null);
  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  // Produk di kategori nonaktif tidak ada di daftar kategori publik: tetap tampilkan kategorinya.
  const options =
    isEdit && !categories.some((c) => c.id === product.category_id)
      ? [{ id: product.category_id, name: product.category_name }, ...categories]
      : categories;

  const patch = isEdit ? buildProductPatch(product, form) : null;
  const changed = isEdit ? Object.keys(patch).length > 0 : true;
  const ready = isProductFormValid(form) && changed;

  async function onSubmit(e) {
    e.preventDefault();
    if (busy || !ready) return;
    setBusy(true);
    setError(null);
    try {
      const res = isEdit
        ? await updateProduct(token, product.id, patch)
        : await createProduct(token, buildProductBody(form));
      setSaved(res.data);
    } catch (err) {
      if (err?.status === 401) {
        onUnauthorized();
        return;
      }
      setError(describeProductError(err));
      setBusy(false);
    }
  }

  if (saved) {
    return (
      <>
        <section className="ticket" aria-live="polite">
          <p className="pill">{isEdit ? "Perubahan disimpan" : "Produk ditambahkan"}</p>
          <p className="ticket__number users__created">{saved.name}</p>
          <p className="muted ticket__name">
            {formatRupiah(saved.price)} · {saved.is_available ? "Tampil di menu" : "Disembunyikan"}
          </p>
        </section>
        {!isEdit && (
          <p className="muted">Stok belum diisi, jadi di menu produk ini tampil "Habis" sampai stoknya tersedia.</p>
        )}
        <button type="button" className="btn btn--block" onClick={onDone}>
          Selesai
        </button>
      </>
    );
  }

  return (
    <>
      <button type="button" className="link-btn" onClick={onBack}>
        ← Kembali
      </button>
      <h1 className="page-title">{isEdit ? "Ubah produk" : "Tambah produk"}</h1>

      <form onSubmit={onSubmit} noValidate>
        {error && (
          <div className="alert" role="alert">
            <p className="alert__title">{error}</p>
          </div>
        )}
        <div className="field">
          <label className="field__label" htmlFor="prod-name">
            Nama produk
          </label>
          <input
            id="prod-name"
            className="input"
            maxLength={MAX_NAME_LENGTH}
            value={form.name}
            onChange={set("name")}
          />
        </div>
        <div className="field">
          <label className="field__label" htmlFor="prod-category">
            Kategori
          </label>
          <select id="prod-category" className="input" value={form.categoryId} onChange={set("categoryId")}>
            <option value="">Pilih kategori</option>
            {options.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="field__label" htmlFor="prod-price">
            Harga jual (Rp)
          </label>
          <input
            id="prod-price"
            className="input"
            inputMode="numeric"
            autoComplete="off"
            placeholder="25000"
            value={form.price}
            onChange={set("price")}
          />
          <p className="muted">{moneyHint(form.price)}</p>
        </div>
        <div className="field">
          <label className="field__label" htmlFor="prod-cost">
            HPP / modal (Rp)
          </label>
          <input
            id="prod-cost"
            className="input"
            inputMode="numeric"
            autoComplete="off"
            placeholder="15000"
            value={form.costPrice}
            onChange={set("costPrice")}
          />
          <p className="muted">{moneyHint(form.costPrice)}</p>
        </div>
        {isSellingAtLoss(form) && (
          <p className="muted">Perhatian: harga jual lebih kecil dari modal, jadi tiap terjual rugi.</p>
        )}
        <div className="field">
          <label className="field__label" htmlFor="prod-desc">
            Deskripsi (opsional)
          </label>
          <input
            id="prod-desc"
            className="input"
            maxLength={1000}
            value={form.description}
            onChange={set("description")}
          />
        </div>
        <div className="field">
          <label className="field__label" htmlFor="prod-image">
            Alamat gambar (opsional)
          </label>
          <input
            id="prod-image"
            className="input"
            inputMode="url"
            autoCapitalize="none"
            maxLength={500}
            placeholder="/images/nasi-goreng.jpg"
            value={form.imageUrl}
            onChange={set("imageUrl")}
          />
        </div>
        <label className="check">
          <input
            type="checkbox"
            checked={form.isAvailable}
            onChange={(e) => setForm((f) => ({ ...f, isAvailable: e.target.checked }))}
          />
          <span>Tampil di menu customer</span>
        </label>
        {!form.isAvailable && (
          <p className="muted">Produk disembunyikan tidak muncul di menu, tapi order lama tetap aman.</p>
        )}
        <div className="row-actions">
          <button type="button" className="btn btn--ghost" disabled={busy} onClick={onBack}>
            Batal
          </button>
          <button type="submit" className="btn" disabled={!ready || busy}>
            {busy ? "Menyimpan…" : "Simpan"}
          </button>
        </div>
      </form>
    </>
  );
}
