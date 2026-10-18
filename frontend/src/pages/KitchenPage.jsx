import { useState } from "react";
import { EmptyState } from "../components/feedback/States";
import StaffHeader from "../components/layout/StaffHeader";
import StaffNav from "../components/layout/StaffNav";
import { describeKitchenError } from "../features/kitchen/errors";
import KitchenOrderCard from "../features/kitchen/KitchenOrderCard";
import { splitQueue } from "../features/kitchen/kitchen";
import RemakePanel from "../features/kitchen/RemakePanel";
import { useKitchenQueue } from "../features/kitchen/useKitchenQueue";
import { useNow } from "../features/kitchen/useNow";
import { markItemReady, startOrder } from "../services/staffApi";
import { useAuth } from "../stores/AuthContext";

// Layar Dapur (wireframes.md #14-#16): antrean masak -> mulai -> item siap / remake.
export default function KitchenPage({ screen }) {
  const { user, token, logout } = useAuth();
  const { status, orders, reload, applyUpdate } = useKitchenQueue(token, { onUnauthorized: logout });
  const now = useNow();
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const [remake, setRemake] = useState(null); // { order, item }

  const { cooking, waiting } = splitQueue(orders);

  // Satu aksi pada satu waktu: mencegah dobel tap saat jaringan lambat.
  async function run(action) {
    if (busy) return;
    setBusy(true);
    setNotice(null);
    try {
      const res = await action();
      applyUpdate(res.data);
    } catch (err) {
      if (err?.status === 401) {
        logout();
        return;
      }
      setNotice(describeKitchenError(err));
      reload();
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <StaffHeader title={screen.title} user={user} onLogout={logout} />
      <main className="container">
        {remake ? (
          <RemakePanel
            order={remake.order}
            item={remake.item}
            token={token}
            onCancel={() => setRemake(null)}
            onDone={(updated) => {
              applyUpdate(updated);
              setRemake(null);
            }}
            onUnauthorized={logout}
          />
        ) : (
          <>
            <StaffNav role={user.role} current={screen.path} />

            {notice && (
              <div className="alert kitchen__alert" role="alert">
                <p className="alert__title">{notice}</p>
              </div>
            )}
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
                title="Belum ada order untuk dimasak."
                hint="Order yang sudah dibayar akan muncul di sini otomatis."
              />
            )}

            {cooking.length > 0 && (
              <section className="kitchen__group" aria-label="Sedang dimasak">
                <h1 className="page-title">Sedang dimasak</h1>
                <ul className="kitchen__list">
                  {cooking.map((o) => (
                    <KitchenOrderCard
                      key={o.order_id}
                      order={o}
                      now={now}
                      busy={busy}
                      onReady={(item) => run(() => markItemReady(token, item.order_item_id))}
                      onRemake={(order, item) => setRemake({ order, item })}
                    />
                  ))}
                </ul>
              </section>
            )}

            {waiting.length > 0 && (
              <section className="kitchen__group" aria-label="Antrean">
                <h2 className="page-title">Antrean</h2>
                <ul className="kitchen__list">
                  {waiting.map((o) => (
                    <KitchenOrderCard
                      key={o.order_id}
                      order={o}
                      now={now}
                      busy={busy}
                      onStart={(order) => run(() => startOrder(token, order.order_id))}
                    />
                  ))}
                </ul>
              </section>
            )}
          </>
        )}
      </main>
    </>
  );
}
