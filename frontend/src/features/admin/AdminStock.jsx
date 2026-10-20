import { useEffect, useState } from "react";
import { EmptyState } from "../../components/feedback/States";
import { pageInfo } from "./admin";
import { stockLabel } from "./stock";
import { useStock } from "./useStock";

export default function AdminStock({ token, categories, filters, onFilters, onAdjust, onUnauthorized }) {
  const { status, items, pagination, reload } = useStock(token, filters, { onUnauthorized });
  const [draft, setDraft] = useState(filters.search);
  const info = pageInfo(pagination, "produk");
  const change = (patch) => onFilters({ ...filters, ...patch, page: 1 });

  // Kalau halaman yang dibuka melewati batas, mundur ke halaman terakhir.
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
      </div>

      {status === "loading" && <p className="muted state">Memuat stok…</p>}
      {status === "error" && (
        <div className="state" role="alert">
          <h2 className="state__title">Stok belum bisa dimuat.</h2>
          <p className="muted">Periksa koneksi, lalu coba lagi.</p>
          <button type="button" className="btn" onClick={reload}>
            Coba lagi
          </button>
        </div>
      )}
      {status === "ready" && items.length === 0 && (
        <EmptyState title="Tidak ada produk." hint="Coba ubah filter atau kata pencarian." />
      )}

      {items.length > 0 && (
        <ul className="list surface">
          {items.map((it) => (
            <li key={it.product_id} className="queue__row">
              <span className="queue__main">
                <span className="queue__name">{it.product_name}</span>
                <span className="muted">
                  Tersedia {it.quantity_available}
                  {it.quantity_reserved > 0 ? ` · Ditahan pesanan ${it.quantity_reserved}` : ""}
                </span>
                <span className="admin__chips">
                  <span className="pill">{it.category_name}</span>
                  {stockLabel(it) && <span className="pill pill--warn">{stockLabel(it)}</span>}
                  {!it.is_available && <span className="pill">Disembunyikan</span>}
                </span>
              </span>
              <button type="button" className="btn btn--sm btn--ghost" onClick={() => onAdjust(it)}>
                Atur stok
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
