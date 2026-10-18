import { useState } from "react";
import { EmptyState } from "../components/feedback/States";
import StaffHeader from "../components/layout/StaffHeader";
import StaffNav from "../components/layout/StaffNav";
import { describePickupError } from "../features/pickup/errors";
import { cleanToken, isPlausibleToken, itemCount, orderFromRow } from "../features/pickup/pickup";
import QrScanner from "../features/pickup/QrScanner";
import { usePickupQueue } from "../features/pickup/usePickupQueue";
import VerifiedPanel from "../features/pickup/VerifiedPanel";
import { verifyPickup } from "../services/staffApi";
import { useAuth } from "../stores/AuthContext";

// Layar Pickup (wireframes.md #19-#22): scan QR -> verifikasi -> serahkan -> selesaikan.
export default function PickupPage({ screen }) {
  const { user, token, logout } = useAuth();
  const { status, orders, reload } = usePickupQueue(token, { onUnauthorized: logout });
  const [scanning, setScanning] = useState(false);
  const [verified, setVerified] = useState(null);
  const [problem, setProblem] = useState(null);
  const [manual, setManual] = useState("");
  const [busy, setBusy] = useState(false);

  async function verify(raw) {
    if (busy) return;
    setScanning(false);
    setProblem(null);
    const pickupToken = cleanToken(raw);
    if (!isPlausibleToken(pickupToken)) {
      setProblem(describePickupError({ code: "PICKUP_NOT_FOUND" }));
      return;
    }
    setBusy(true);
    try {
      const res = await verifyPickup(token, pickupToken);
      setVerified(res.data);
    } catch (err) {
      if (err?.status === 401) {
        logout();
        return;
      }
      setProblem(describePickupError(err));
    } finally {
      setBusy(false);
    }
  }

  function onManualSubmit(e) {
    e.preventDefault();
    const value = manual;
    setManual("");
    verify(value);
  }

  function renderBody() {
    if (verified) {
      return (
        <VerifiedPanel
          order={verified}
          token={token}
          onCancel={() => setVerified(null)}
          onFinished={() => {
            setVerified(null);
            reload();
          }}
          onUnauthorized={logout}
        />
      );
    }
    if (problem) {
      return (
        <section className="state" role="alert">
          <h1 className="state__title">{problem.title}</h1>
          <p className="muted">{problem.message}</p>
          <button type="button" className="btn" onClick={() => setProblem(null)}>
            Tutup
          </button>
        </section>
      );
    }
    if (scanning) return <QrScanner onDetected={verify} onCancel={() => setScanning(false)} />;

    return (
      <>
        <StaffNav role={user.role} current={screen.path} />
        <h1 className="page-title">Pickup</h1>

        {busy && (
          <p className="muted" role="status">
            Memeriksa token…
          </p>
        )}
        <button type="button" className="btn btn--block" disabled={busy} onClick={() => setScanning(true)}>
          Scan QR pickup
        </button>

        <details className="manual">
          <summary>Tempel token manual</summary>
          <form onSubmit={onManualSubmit}>
            <input
              className="input"
              aria-label="Token pickup dari customer"
              placeholder="Token dari customer"
              autoComplete="off"
              autoCapitalize="none"
              spellCheck={false}
              value={manual}
              onChange={(e) => setManual(e.target.value)}
            />
            <button type="submit" className="btn btn--sm" disabled={busy || !manual.trim()}>
              Verifikasi
            </button>
          </form>
        </details>

        <h2 className="page-title">Siap diambil</h2>
        {status === "stale" && (
          <p className="muted queue__note" role="status">
            Gagal memperbarui daftar. Mencoba lagi otomatis…
          </p>
        )}
        {status === "loading" && orders.length === 0 && <p className="muted state">Memuat daftar…</p>}
        {status === "error" && (
          <div className="state" role="alert">
            <h2 className="state__title">Daftar belum bisa dimuat.</h2>
            <p className="muted">Periksa koneksi, lalu coba lagi.</p>
            <button type="button" className="btn" onClick={reload}>
              Coba lagi
            </button>
          </div>
        )}
        {status === "ready" && orders.length === 0 && (
          <EmptyState
            title="Belum ada pesanan siap diambil."
            hint="Pesanan yang selesai dimasak dapur akan muncul di sini otomatis."
          />
        )}
        {orders.length > 0 && (
          <ul className="list surface">
            {orders.map((o) => (
              <li key={o.pickup_id} className="queue__row">
                <span className="queue__no">{o.order_number}</span>
                <span className="queue__main">
                  <span className="queue__name">{o.customer_name}</span>
                  <span className="muted">
                    {itemCount(o.items)} item{o.status === "OVERDUE" ? " · Terlambat diambil" : ""}
                  </span>
                </span>
                {o.verified ? (
                  <button type="button" className="btn btn--sm" onClick={() => setVerified(orderFromRow(o))}>
                    Selesaikan
                  </button>
                ) : (
                  <span className="pill">Belum scan</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </>
    );
  }

  return (
    <>
      <StaffHeader title={screen.title} user={user} onLogout={logout} />
      <main className="container">{renderBody()}</main>
    </>
  );
}
