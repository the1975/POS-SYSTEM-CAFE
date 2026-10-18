import { useState } from "react";
import { EmptyState } from "../components/feedback/States";
import StaffHeader from "../components/layout/StaffHeader";
import StaffNav from "../components/layout/StaffNav";
import CashPaymentPanel from "../features/cashier/CashPaymentPanel";
import { useWaitingCash } from "../features/cashier/useWaitingCash";
import { useAuth } from "../stores/AuthContext";
import { formatRupiah } from "../utils/format";

// Layar Kasir (wireframes.md #17-#18): antrean order tunai -> buka -> terima uang -> konfirmasi.
export default function CashierPage({ screen }) {
  const { user, token, logout } = useAuth();
  const [draft, setDraft] = useState("");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const { status, orders, reload } = useWaitingCash(token, search, { onUnauthorized: logout });

  function onSearch(e) {
    e.preventDefault();
    setSearch(draft.trim());
  }

  function finish() {
    setSelected(null);
    reload();
  }

  return (
    <>
      <StaffHeader title={screen.title} user={user} onLogout={logout} />
      <main className="container">
        {selected ? (
          <CashPaymentPanel
            key={selected.order_id}
            order={selected}
            token={token}
            onBack={() => setSelected(null)}
            onDone={finish}
            onUnauthorized={logout}
          />
        ) : (
          <>
            <StaffNav role={user.role} current={screen.path} />
            <h1 className="page-title">Menunggu bayar tunai</h1>

            <form className="searchbar" onSubmit={onSearch} role="search">
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
                hint={
                  search
                    ? "Tidak ada order tunai yang cocok dengan pencarianmu."
                    : "Order tunai baru akan muncul di sini otomatis."
                }
              />
            )}

            {orders.length > 0 && (
              <ul className="list surface">
                {orders.map((o) => (
                  <li key={o.order_id} className="queue__row">
                    <span className="queue__no">{o.order_number}</span>
                    <span className="queue__main">
                      <span className="queue__name">{o.customer_name}</span>
                      <span className="muted">{formatRupiah(o.total)}</span>
                    </span>
                    <button type="button" className="btn btn--sm" onClick={() => setSelected(o)}>
                      Buka
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </main>
    </>
  );
}
