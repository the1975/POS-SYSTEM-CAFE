import { useEffect } from "react";
import { EmptyState } from "../../components/feedback/States";
import { formatRupiah } from "../../utils/format";
import { pageInfo } from "./admin";
import AdminSearch from "./AdminSearch";
import { groupBy } from "./group";
import { useAdminProducts } from "./useAdminProducts";

// Daftar produk: dikelompokkan per kategori, cukup cari nama produk.
export default function AdminProducts({ token, filters, onFilters, onEdit, onUnauthorized }) {
  const { status, products, pagination, reload } = useAdminProducts(token, filters, { onUnauthorized });
  const info = pageInfo(pagination, "produk");
  const groups = groupBy(products, (p) => p.category_name);

  // Kalau halaman yang dibuka melewati batas (mis. data berkurang), mundur ke halaman terakhir.
  useEffect(() => {
    if (pagination && pagination.total_pages > 0 && filters.page > pagination.total_pages) {
      onFilters({ ...filters, page: pagination.total_pages });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination]);

  return (
    <>
      <AdminSearch label="Cari nama produk" placeholder="Nama produk" filters={filters} onFilters={onFilters} />

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
        <EmptyState title="Tidak ada produk." hint="Coba kata pencarian lain." />
      )}

      {groups.map((g) => (
        <section key={g.label} className="ugroup" aria-label={g.label}>
          <h2 className="ugroup__title">
            {g.label} · {g.items.length}
          </h2>
          <ul className="list surface ugroup__list">
            {g.items.map((p) => (
              <li key={p.id}>
                <button
                  type="button"
                  className={`urow${p.is_available ? "" : " urow--off"}`}
                  aria-label={`Ubah ${p.name}`}
                  onClick={() => onEdit(p)}
                >
                  <span className="urow__avatar urow__avatar--sq" aria-hidden="true">
                    {p.name.charAt(0).toUpperCase()}
                  </span>
                  <span className="queue__main">
                    <span className="queue__name">{p.name}</span>
                    <span className="muted">
                      {formatRupiah(p.price)} · HPP {formatRupiah(p.cost_price)}
                    </span>
                  </span>
                  {!p.is_available && <span className="pill pill--warn">Disembunyikan</span>}
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
