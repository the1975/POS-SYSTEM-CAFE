import { useState } from "react";
import { remakeItem } from "../../services/staffApi";
import { describeKitchenError } from "./errors";
import { REMAKE_REASONS } from "./kitchen";

// Wireframes.md #16: order dan item yang sama dibuat ulang, alasan wajib, catatan opsional.
export default function RemakePanel({ order, item, token, onCancel, onDone, onUnauthorized }) {
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    if (busy || !reason) return;
    setBusy(true);
    setError(null);
    try {
      const res = await remakeItem(token, item.order_item_id, { reason, notes });
      onDone(res.data);
    } catch (err) {
      if (err?.status === 401) {
        onUnauthorized();
        return;
      }
      setError(describeKitchenError(err));
      setBusy(false);
    }
  }

  return (
    <>
      <h1 className="page-title">Remake item</h1>
      <section className="surface summary" aria-label="Item yang dibuat ulang">
        <div className="summary__row">
          <span>Order</span>
          <strong>{order.order_number}</strong>
        </div>
        <div className="summary__row summary__row--item">
          <span>Item</span>
          <strong>
            {item.name} ×{item.quantity}
          </strong>
        </div>
      </section>

      <form onSubmit={onSubmit} noValidate className="remake__form">
        {error && (
          <div className="alert" role="alert">
            <p className="alert__title">{error}</p>
          </div>
        )}
        <div className="field">
          <label className="field__label" htmlFor="remake-reason">
            Alasan
          </label>
          <select
            id="remake-reason"
            className="input"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          >
            <option value="">Pilih alasan…</option>
            {REMAKE_REASONS.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="field__label" htmlFor="remake-notes">
            Catatan (opsional)
          </label>
          <textarea
            id="remake-notes"
            className="input input--area"
            maxLength={500}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>
        <div className="row-actions">
          <button type="button" className="btn btn--ghost" disabled={busy} onClick={onCancel}>
            Batal
          </button>
          <button type="submit" className="btn" disabled={busy || !reason}>
            {busy ? "Memproses…" : "Konfirmasi remake"}
          </button>
        </div>
      </form>
    </>
  );
}
