import { useEffect } from "react";
import { EmptyState } from "../../components/feedback/States";
import { pageInfo } from "./admin";
import AdminSearch from "./AdminSearch";
import { groupBy } from "./group";
import { stockLabel } from "./stock";
import { useStock } from "./useStock";

// Daftar stok: dikelompokkan per kategori; stok menipis/habis diberi label mencolok.
export default function AdminStock({ token, filters, onFilters, onAdjust, onUnauthorized }) {
  const { status, items, pagination, reload } = useStock(token, filters, { onUnauthorized });
  const info = pageInfo(pagination, "produk");
  const groups = groupBy(items, (it) => it.category_name);

  // Kalau halaman yang dibuka melewati batas, mundur ke halaman terakhir.
  useEffect(() => {
    if (pagination && pagination.total_pages > 0 && filters.page > pagination.total_pages) {
      onFilters({ ...filters, page: pagination.total_pages });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination]);

  return (
    <>
      <AdminSearch label="Cari nama produk" placeholder="Nama produk" filters={filters} onFilters={onFilters} />

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
        <EmptyState title="Tidak ada produk." hint="Coba kata pencarian lain." />
      )}

      {groups.map((g) => (
        <section key={g.label} className="ugroup" aria-label={g.label}>
          <h2 className="ugroup__title">
            {g.label} · {g.items.length}
          </h2>
          <ul className="list surface ugroup__list">
            {g.items.map((it) => (
              <li key={it.product_id}>
                <button
                  type="button"
                  className={`urow${it.is_available ? "" : " urow--off"}`}
                  aria-label={`Atur stok ${it.product_name}`}
                  onClick={() => onAdjust(it)}
                >
                  <span className="urow__avatar urow__avatar--sq" aria-hidden="true">
                    {it.product_name.charAt(0).toUpperCase()}
                  </span>
                  <span className="queue__main">
                    <span className="queue__name">{it.product_name}</span>
                    {(it.quantity_reserved > 0 || !it.is_available) && (
                      <span className="muted">
                        {it.quantity_reserved > 0 ? `Ditahan pesanan ${it.quantity_reserved}` : "Disembunyikan"}
                      </span>
                    )}
                  </span>
                  {stockLabel(it) && <span className="pill pill--warn">{stockLabel(it)}</span>}
                  <span className="urow__qty">
                    <strong>{it.quantity_available}</strong>
                    <span className="muted">tersedia</span>
                  </span>
                  <svg className="urow__go" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M9 6l6 6-6 6" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        </section>
      ))}

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
