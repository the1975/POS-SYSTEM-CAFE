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
import AdminSearch from "./AdminSearch";
import FilterSheet from "./FilterSheet";
import { useAdminOrders } from "./useAdminOrders";

// Status yang perlu perhatian ditandai merah.
const WARN = new Set(["CANCELLED", "OVERDUE", "FAILED", "REFUND_FAILED"]);
const short = (options) => options.map((o) => (o.value === "" ? { ...o, label: "Semua" } : o));
const FILTER_GROUPS = [
  { key: "status", label: "Status order", options: short(STATUS_FILTERS) },
  { key: "paymentStatus", label: "Status bayar", options: short(PAYMENT_FILTERS) },
];

export default function AdminOrders({ token, filters, onFilters, onRefund, onUnauthorized }) {
  const { status, orders, pagination, reload } = useAdminOrders(token, filters, { onUnauthorized });
  const [sheetOpen, setSheetOpen] = useState(false);
  const info = pageInfo(pagination);
  const filterActive = Boolean(filters.status || filters.paymentStatus);

  // Setelah refund, halaman terakhir bisa kosong: mundur ke halaman terakhir yang ada.
  useEffect(() => {
    if (pagination && pagination.total_pages > 0 && filters.page > pagination.total_pages) {
      onFilters({ ...filters, page: pagination.total_pages });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination]);

  return (
    <>
      <div className="usearchrow">
        <AdminSearch label="Cari nomor order atau nama" placeholder="Nomor order atau nama" filters={filters} onFilters={onFilters} />
        <button type="button" className="ufilter" aria-label="Filter order" aria-haspopup="dialog" onClick={() => setSheetOpen(true)}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <path d="M4 6h16M7 12h10M10 18h4" />
          </svg>
          {filterActive && <span className="ufilter__dot" aria-hidden="true" />}
        </button>
      </div>
      <FilterSheet
        open={sheetOpen}
        title="Filter order"
        groups={FILTER_GROUPS}
        values={{ status: filters.status, paymentStatus: filters.paymentStatus }}
        onClose={() => setSheetOpen(false)}
        onApply={(d) => {
          onFilters({ ...filters, status: d.status, paymentStatus: d.paymentStatus, page: 1 });
          setSheetOpen(false);
        }}
      />

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
        <EmptyState title="Tidak ada order." hint="Coba filter atau kata pencarian lain." />
      )}

      {orders.length > 0 && (
        <ul className="list surface ugroup__list">
          {orders.map((o) => (
            <li key={o.order_id} className="orow">
              <div className="orow__top">
                <span className="orow__no">{o.order_number}</span>
                <span className="queue__main">
                  <span className="queue__name">{o.customer_name}</span>
                  <span className="muted">{formatShortDateTime(o.created_at)}</span>
                </span>
                <strong className="orow__total">{formatRupiah(o.total)}</strong>
              </div>
              <div className="orow__meta">
                <span className={`pill${WARN.has(o.status) ? " pill--warn" : ""}`}>{orderStatusLabel(o.status)}</span>
                <span className={`pill${WARN.has(o.payment_status) ? " pill--warn" : ""}`}>
                  {paymentStatusLabel(o.payment_status)}
                </span>
                {canRefund(o) && (
                  <button type="button" className="btn btn--sm btn--ghost orow__refund" onClick={() => onRefund(o)}>
                    Refund
                  </button>
                )}
              </div>
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
