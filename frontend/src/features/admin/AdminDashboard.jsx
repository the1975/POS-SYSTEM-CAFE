import { useState } from "react";
import { EmptyState } from "../../components/feedback/States";
import { formatRupiah } from "../../utils/format";
import { DASHBOARD_RANGES, busiestHour, formatHour, hasSales, peakBars, rangeLabel } from "./dashboard";
import { useDashboard } from "./useDashboard";

export default function AdminDashboard({ token, onUnauthorized }) {
  const [rangeId, setRangeId] = useState("today");
  const { status, range, summary, top, hours, reload } = useDashboard(token, rangeId, { onUnauthorized });
  const busiest = busiestHour(hours);

  return (
    <>
      <nav className="chips" aria-label="Rentang waktu">
        {DASHBOARD_RANGES.map((r) => (
          <button
            key={r.id}
            type="button"
            className="chip"
            aria-pressed={rangeId === r.id}
            onClick={() => setRangeId(r.id)}
          >
            {r.label}
          </button>
        ))}
      </nav>
      {range && <p className="muted">{rangeLabel(range.startDate, range.endDate)}</p>}

      {status === "loading" && <p className="muted state">Memuat laporan…</p>}
      {status === "error" && (
        <div className="state" role="alert">
          <h2 className="state__title">Laporan belum bisa dimuat.</h2>
          <p className="muted">Periksa koneksi, lalu coba lagi.</p>
          <button type="button" className="btn" onClick={reload}>
            Coba lagi
          </button>
        </div>
      )}

      {status === "ready" && !hasSales(summary) && (
        <EmptyState title="Belum ada penjualan." hint="Hanya order yang sudah lunas yang dihitung." />
      )}

      {status === "ready" && hasSales(summary) && (
        <>
          <div className="dash__cards">
            <div className="surface dash__card">
              <span className="muted">Omzet</span>
              <strong className="dash__value">{formatRupiah(summary.revenue)}</strong>
            </div>
            <div className="surface dash__card">
              <span className="muted">Order</span>
              <strong className="dash__value">{summary.orders}</strong>
            </div>
            <div className="surface dash__card">
              <span className="muted">Unit terjual</span>
              <strong className="dash__value">{summary.units_sold}</strong>
            </div>
            <div className="surface dash__card">
              <span className="muted">Rata-rata per order</span>
              <strong className="dash__value">{formatRupiah(summary.average_order_value)}</strong>
            </div>
          </div>

          <h2 className="dash__title">Produk terlaris</h2>
          <ul className="list surface">
            {top.map((p, i) => (
              <li key={p.product_id} className="queue__row">
                <span className="dash__rank">{i + 1}</span>
                <span className="queue__main">
                  <span className="queue__name">{p.product_name}</span>
                  <span className="muted">
                    {p.units_sold} terjual · {formatRupiah(p.revenue)}
                  </span>
                </span>
              </li>
            ))}
          </ul>

          <h2 className="dash__title">Jam ramai</h2>
          {busiest && <p className="muted">Paling ramai: {busiest}</p>}
          <div className="surface">
            <div className="dash__bars" role="img" aria-label="Grafik jumlah order per jam">
              {peakBars(hours).map((b) => (
                <span
                  key={b.hour}
                  className={b.pct === 0 ? "dash__bar dash__bar--zero" : "dash__bar"}
                  style={b.pct === 0 ? undefined : { height: `${b.pct}%` }}
                  title={`${formatHour(b.hour)}: ${b.orders} order`}
                />
              ))}
            </div>
            <div className="dash__axis" aria-hidden="true">
              <span>00.00</span>
              <span>06.00</span>
              <span>12.00</span>
              <span>18.00</span>
            </div>
          </div>
        </>
      )}
    </>
  );
}
