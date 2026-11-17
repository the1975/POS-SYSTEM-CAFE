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
  const [tab, setTab] = useState(null); // null = otomatis: Dimasak kalau ada, kalau tidak Antre

  const { cooking, waiting } = splitQueue(orders);
  const active = tab ?? (cooking.length > 0 ? "cooking" : "waiting");

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
      <main className="container container--wide has-nav">
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
            <h1 className="page-title">Antrean dapur</h1>
            <div className="seg seg--narrow" role="group" aria-label="Tampilan antrean">
              <button type="button" className="seg__item" aria-pressed={active === "waiting"} onClick={() => setTab("waiting")}>
                Antre · {waiting.length}
              </button>
              <button type="button" className="seg__item" aria-pressed={active === "cooking"} onClick={() => setTab("cooking")}>
                Dimasak · {cooking.length}
              </button>
            </div>

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
            <div className="kcols">
              {[
                { key: "waiting", title: "Antre", list: waiting },
                { key: "cooking", title: "Dimasak", list: cooking },
              ].map((col) => (
                <section key={col.key} className={`kcol${active === col.key ? " is-active" : ""}`} aria-label={col.title}>
                  <h2 className="kcol__title">
                    {col.title} <span className="count">{col.list.length}</span>
                  </h2>
                  {status === "ready" && col.list.length === 0 && (
                    <EmptyState
                      title={col.key === "cooking" ? "Belum ada yang dimasak." : "Antrean kosong."}
                      hint="Order yang sudah dibayar muncul di sini otomatis."
                    />
                  )}
                  {col.list.length > 0 && (
                    <ul className="kitchen__list kitchen__list--top">
                      {col.list.map((o) =>
                        col.key === "cooking" ? (
                          <KitchenOrderCard
                            key={o.order_id}
                            order={o}
                            now={now}
                            busy={busy}
                            onReady={(item) => run(() => markItemReady(token, item.order_item_id))}
                            onRemake={(order, item) => setRemake({ order, item })}
                          />
                        ) : (
                          <KitchenOrderCard
                            key={o.order_id}
                            order={o}
                            now={now}
                            busy={busy}
                            onStart={(order) => run(() => startOrder(token, order.order_id))}
                          />
                        ),
                      )}
                    </ul>
                  )}
                </section>
              ))}
            </div>
          </>
        )}
      </main>
      <StaffNav role={user.role} />
    </>
  );
}
