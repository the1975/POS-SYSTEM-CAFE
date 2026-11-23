import { useState } from "react";
import { EmptyState } from "../../components/feedback/States";
import { formatRupiah } from "../../utils/format";
import { DASHBOARD_RANGES, busiestHour, formatHour, hasSales, peakBars, rangeLabel } from "./dashboard";
import { useDashboard } from "./useDashboard";

function Svg({ children }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {children}
    </svg>
  );
}

const kpis = (s) => [
  {
    label: "Omzet",
    value: formatRupiah(s.revenue),
    icon: <><rect x="3" y="6" width="18" height="13" rx="3" /><path d="M16 12h2" /></>,
  },
  { label: "Order", value: s.orders, icon: <path d="M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6" /> },
  {
    label: "Unit terjual",
    value: s.units_sold,
    icon: <><path d="M5 8h11v6a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4V8z" /><path d="M16 10h1.5a2.5 2.5 0 0 1 0 5H16M8 3v2M12 3v2" /></>,
  },
  { label: "Rata-rata order", value: formatRupiah(s.average_order_value), icon: <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" /> },
  {
    label: "Laba kotor",
    value: formatRupiah(s.gross_profit ?? 0),
    note: "Penjualan tanpa pajak dikurangi HPP",
    wide: true,
    icon: <path d="M3 17l6-6 4 4 8-8M15 7h6v6" />,
  },
];

export default function AdminDashboard({ token, onUnauthorized }) {
  const [rangeId, setRangeId] = useState("today");
  const { status, range, summary, top, hours, reload } = useDashboard(token, rangeId, { onUnauthorized });
  const busiest = busiestHour(hours);
  const bars = peakBars(hours);
  const maxOrders = Math.max(0, ...bars.map((b) => b.orders));
  const maxUnits = Math.max(1, ...top.map((p) => p.units_sold));

  return (
    <>
      <div className="dash__filter">
        <nav className="seg" aria-label="Rentang waktu">
          {DASHBOARD_RANGES.map((r) => (
            <button
              key={r.id}
              type="button"
              className="seg__item"
              aria-pressed={rangeId === r.id}
              onClick={() => setRangeId(r.id)}
            >
              {r.label}
            </button>
          ))}
        </nav>
        {range && range.startDate !== range.endDate && (
          <p className="dash__range">{rangeLabel(range.startDate, range.endDate)}</p>
        )}
      </div>

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
            {kpis(summary).map((k) => (
              <div key={k.label} className={`surface dash__card${k.wide ? " dash__card--wide" : ""}`}>
                <div className="dash__head">
                  <span className="muted">{k.label}</span>
                  <span className="dash__icon"><Svg>{k.icon}</Svg></span>
                </div>
                <strong className="dash__value">{k.value}</strong>
                {k.note && <span className="muted">{k.note}</span>}
              </div>
            ))}
          </div>

          <section className="surface dash__panel">
            <h2 className="dash__title">Produk terlaris</h2>
            <ol className="dash__top">
              {top.map((p, i) => (
                <li key={p.product_id}>
                  <span className="dash__rank">{i + 1}</span>
                  <div className="dash__topbody">
                    <div className="dash__toprow">
                      <span className="queue__name">{p.product_name}</span>
                      <span className="muted">{p.units_sold} unit</span>
                    </div>
                    <div className="dash__meter">
                      <span style={{ width: `${(p.units_sold / maxUnits) * 100}%` }} />
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </section>

          <section className="surface dash__panel">
            <h2 className="dash__title">Jam ramai</h2>
            {busiest && <p className="muted">Paling ramai: {busiest}</p>}
            <div className="dash__bars" role="img" aria-label="Grafik jumlah order per jam">
              {bars.map((b) => (
                <span
                  key={b.hour}
                  className={`dash__bar${b.pct === 0 ? " dash__bar--zero" : b.orders === maxOrders ? " dash__bar--peak" : ""}`}
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
          </section>
        </>
      )}
    </>
  );
}
