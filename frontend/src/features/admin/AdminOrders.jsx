import { useEffect, useState } from "react";
import { EmptyState } from "../../components/feedback/States";
import { formatRupiah } from "../../utils/format";
import {
  PAYMENT_FILTERS,
  STATUS_FILTERS,
  canRefund,
  formatShortDateTime,
  orderStatusLabel,
  pageInfo,
  paymentStatusLabel,
} from "./admin";
import { useAdminOrders } from "./useAdminOrders";

export default function AdminOrders({ token, filters, onFilters, onRefund, onUnauthorized }) {
  const { status, orders, pagination, reload } = useAdminOrders(token, filters, { onUnauthorized });
  const [draft, setDraft] = useState(filters.search);
  const info = pageInfo(pagination);

  // Setelah refund, halaman terakhir bisa kosong: mundur ke halaman terakhir yang ada.
  useEffect(() => {
    if (pagination && pagination.total_pages > 0 && filters.page > pagination.total_pages) {
      onFilters({ ...filters, page: pagination.total_pages });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination]);

  const change = (patch) => onFilters({ ...filters, ...patch, page: 1 });

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
          aria-label="Cari nomor order atau nama"
          placeholder="Nomor order atau nama"
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
          aria-label="Filter status order"
          value={filters.status}
          onChange={(e) => change({ status: e.target.value })}
        >
          {STATUS_FILTERS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <select
          className="input"
          aria-label="Filter status pembayaran"
          value={filters.paymentStatus}
          onChange={(e) => change({ paymentStatus: e.target.value })}
        >
          {PAYMENT_FILTERS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      {status === "stale" && (
        <p className="muted queue__note" role="status">
          Gagal memperbarui daftar. Mencoba lagi otomatis…
        </p>
      )}
      {status === "loading" && orders.length === 0 && <p className="muted state">Memuat order…</p>}
      {status === "error" && (
        <div className="state" role="alert">
          <h2 className="state__title">Order belum bisa dimuat.</h2>
          <p className="muted">Periksa koneksi, lalu coba lagi.</p>
          <button type="button" className="btn" onClick={reload}>
            Coba lagi
          </button>
        </div>
      )}
      {status === "ready" && orders.length === 0 && (
        <EmptyState
          title="Tidak ada order."
          hint="Coba ubah filter atau kata pencarian."
        />
      )}

      {orders.length > 0 && (
        <ul className="list surface">
          {orders.map((o) => (
            <li key={o.order_id} className="queue__row">
              <span className="queue__no">{o.order_number}</span>
              <span className="queue__main">
                <span className="queue__name">{o.customer_name}</span>
                <span className="muted">
                  {formatRupiah(o.total)} · {formatShortDateTime(o.created_at)}
                </span>
                <span className="admin__chips">
                  <span className="pill">{orderStatusLabel(o.status)}</span>
                  <span className="pill">{paymentStatusLabel(o.payment_status)}</span>
                </span>
              </span>
              {canRefund(o) && (
                <button type="button" className="btn btn--sm btn--ghost" onClick={() => onRefund(o)}>
                  Refund
                </button>
              )}
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
