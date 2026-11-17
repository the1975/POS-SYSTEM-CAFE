import { useState } from "react";
import { EmptyState } from "../components/feedback/States";
import StaffHeader from "../components/layout/StaffHeader";
import StaffNav from "../components/layout/StaffNav";
import AdminSearch from "../features/admin/AdminSearch";
import CashPaymentPanel from "../features/cashier/CashPaymentPanel";
import { useWaitingCash } from "../features/cashier/useWaitingCash";
import { useAuth } from "../stores/AuthContext";
import { formatRupiah } from "../utils/format";

// Layar Kasir (wireframes.md #17-#18): antrean order tunai -> buka -> terima uang -> konfirmasi.
export default function CashierPage({ screen }) {
  const { user, token, logout } = useAuth();
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const { status, orders, reload } = useWaitingCash(token, search, { onUnauthorized: logout });

  function finish() {
    setSelected(null);
    reload();
  }

  return (
    <>
      <StaffHeader title={screen.title} user={user} onLogout={logout} />
      <main className="container container--wide has-nav">
        <div className="split">
          <section className={`split__list${selected ? " is-away" : ""}`}>
            <div className="titlebar">
              <h1 className="page-title">Menunggu bayar tunai</h1>
              {orders.length > 0 && <span className="count">{orders.length}</span>}
            </div>

            <AdminSearch
              label="Cari nomor order atau nama"
              placeholder="Nomor order atau nama"
              filters={{ search }}
              onFilters={(f) => setSearch(f.search)}
            />

            {status === "stale" && (
              <p className="muted queue__note" role="status">
                Gagal memperbarui antrean. Mencoba lagi otomatis…
              </p>
            )}

            {status === "loading" && orders.length === 0 && (
              <p className="muted state">Memuat antrean…</p>
            )}

            {status === "error" && (
              <div className="state" role="alert">
                <h2 className="state__title">Antrean belum bisa dimuat.</h2>
                <p className="muted">Periksa koneksi, lalu coba lagi.</p>
                <button type="button" className="btn" onClick={reload}>
                  Coba lagi
                </button>
              </div>
            )}

            {status === "ready" && orders.length === 0 && (
              <EmptyState
                title="Tidak ada yang menunggu bayar."
                hint={search ? "Tidak ada order yang cocok." : "Order tunai baru muncul di sini otomatis."}
              />
            )}

            {orders.length > 0 && (
              <ul className="list surface ugroup__list">
                {orders.map((o) => (
                  <li key={o.order_id}>
                    <button
                      type="button"
                      className="urow"
                      aria-label={`Buka order ${o.order_number} atas nama ${o.customer_name}`}
                      onClick={() => setSelected(o)}
                    >
                      <span className="orow__no">{o.order_number}</span>
                      <span className="queue__main">
                        <span className="queue__name">{o.customer_name}</span>
                      </span>
                      <strong>{formatRupiah(o.total)}</strong>
                      <svg className="urow__go" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d="M9 6l6 6-6 6" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
          {selected ? (
            <section className="split__panel">
              <CashPaymentPanel
                key={selected.order_id}
                order={selected}
                token={token}
                onBack={() => setSelected(null)}
                onDone={finish}
                onUnauthorized={logout}
              />
            </section>
          ) : (
            <section className="surface split__empty">
              <p className="muted">Pilih order di sebelah kiri untuk menerima pembayaran.</p>
            </section>
          )}
        </div>
      </main>
      <StaffNav role={user.role} />
    </>
  );
}
