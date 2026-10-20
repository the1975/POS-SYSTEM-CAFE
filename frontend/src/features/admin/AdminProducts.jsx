import { useEffect, useState } from "react";
import { EmptyState } from "../../components/feedback/States";
import { formatRupiah } from "../../utils/format";
import { pageInfo } from "./admin";
import { PRODUCT_STATUS_FILTERS } from "./products";
import { useAdminProducts } from "./useAdminProducts";

export default function AdminProducts({ token, categories, filters, onFilters, onEdit, onUnauthorized }) {
  const { status, products, pagination, reload } = useAdminProducts(token, filters, { onUnauthorized });
  const [draft, setDraft] = useState(filters.search);
  const info = pageInfo(pagination, "produk");
  const change = (patch) => onFilters({ ...filters, ...patch, page: 1 });

  // Kalau halaman yang dibuka melewati batas (mis. data berkurang), mundur ke halaman terakhir.
  useEffect(() => {
    if (pagination && pagination.total_pages > 0 && filters.page > pagination.total_pages) {
      onFilters({ ...filters, page: pagination.total_pages });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination]);

  return (
    <>
      <form
        className="searchbar"
        role="search"
        onSubmit={(e) => {
          e.preventDefault();
          change({ search: draft.trim() });
        }}
      >
        <input
          className="input"
          type="search"
          aria-label="Cari nama produk"
          placeholder="Nama produk"
          maxLength={100}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <button type="submit" className="btn btn--sm">
          Cari
        </button>
      </form>

      <div className="admin__filters">
        <select
          className="input"
          aria-label="Filter kategori"
          value={filters.categoryId}
          onChange={(e) => change({ categoryId: e.target.value })}
        >
          <option value="">Semua kategori</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          className="input"
          aria-label="Filter status produk"
          value={filters.isAvailable}
          onChange={(e) => change({ isAvailable: e.target.value })}
        >
          {PRODUCT_STATUS_FILTERS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      {status === "loading" && <p className="muted state">Memuat produk…</p>}
      {status === "error" && (
        <div className="state" role="alert">
          <h2 className="state__title">Produk belum bisa dimuat.</h2>
          <p className="muted">Periksa koneksi, lalu coba lagi.</p>
          <button type="button" className="btn" onClick={reload}>
            Coba lagi
          </button>
        </div>
      )}
      {status === "ready" && products.length === 0 && (
        <EmptyState title="Tidak ada produk." hint="Coba ubah filter atau kata pencarian." />
      )}

      {products.length > 0 && (
        <ul className="list surface">
          {products.map((p) => (
            <li key={p.id} className="queue__row">
              <span className="queue__main">
                <span className="queue__name">{p.name}</span>
                <span className="muted">
                  {formatRupiah(p.price)} · HPP {formatRupiah(p.cost_price)}
                </span>
                <span className="admin__chips">
                  <span className="pill">{p.category_name}</span>
                  {!p.is_available && <span className="pill pill--warn">Disembunyikan</span>}
                </span>
              </span>
              <button type="button" className="btn btn--sm btn--ghost" onClick={() => onEdit(p)}>
                Ubah
              </button>
            </li>
          ))}
        </ul>
      )}

      {info.label && (
        <div className="admin__pager">
          <button
            type="button"
            className="btn btn--sm btn--ghost"
            disabled={!info.hasPrev}
            onClick={() => onFilters({ ...filters, page: filters.page - 1 })}
          >
            Sebelumnya
          </button>
          <span className="muted">{info.label}</span>
          <button
            type="button"
            className="btn btn--sm btn--ghost"
            disabled={!info.hasNext}
            onClick={() => onFilters({ ...filters, page: filters.page + 1 })}
          >
            Berikutnya
          </button>
        </div>
      )}
    </>
  );
}
