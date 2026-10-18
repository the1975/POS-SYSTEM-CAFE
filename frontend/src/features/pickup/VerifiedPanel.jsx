import { useState } from "react";
import { completePickup } from "../../services/staffApi";
import { statusLabel } from "../orders/statusLabels";
import { describePickupError } from "./errors";
import { itemCount } from "./pickup";

// Wireframes.md #20: order valid -> petugas menyerahkan pesanan -> Selesaikan Pickup.
export default function VerifiedPanel({ order, token, onFinished, onCancel, onUnauthorized }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [done, setDone] = useState(false);

  async function onComplete() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      await completePickup(token, order.pickup_id);
      setDone(true);
    } catch (err) {
      if (err?.status === 401) {
        onUnauthorized();
        return;
      }
      setError(describePickupError(err).message);
      setBusy(false);
    }
  }

  if (done) {
    return (
      <>
        <section className="ticket" aria-live="polite">
          <p className="pill">Pickup selesai</p>
          <p className="ticket__number">{order.order_number}</p>
          <p className="muted ticket__name">{order.customer_name}</p>
        </section>
        <button type="button" className="btn btn--block" onClick={onFinished}>
          Selesai
        </button>
      </>
    );
  }

  return (
    <>
      <section className="ticket">
        <p className="pill">✓ Order valid</p>
        <p className="ticket__number">{order.order_number}</p>
        <p className="muted ticket__name">{order.customer_name}</p>
      </section>

      <ul className="list surface">
        {order.items.map((item, i) => (
          <li key={i} className="line line--simple">
            <span>{item.name}</span>
            <span className="muted">× {item.quantity}</span>
          </li>
        ))}
      </ul>
      <p className="muted pickup__meta">
        {itemCount(order.items)} item · {statusLabel(order.status)}
        {order.payment_status ? ` · Pembayaran: ${order.payment_status === "PAID" ? "Lunas" : order.payment_status}` : ""}
      </p>

      {error && (
        <div className="alert" role="alert">
          <p className="alert__title">{error}</p>
        </div>
      )}

      <button type="button" className="btn btn--block" disabled={busy} onClick={onComplete}>
        {busy ? "Memproses…" : "Selesaikan pickup"}
      </button>
      <button type="button" className="btn btn--ghost btn--block" disabled={busy} onClick={onCancel}>
        Batal
      </button>
    </>
  );
}
