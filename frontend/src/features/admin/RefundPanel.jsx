import { useState } from "react";
import { refundPayment } from "../../services/staffApi";
import { formatRupiah } from "../../utils/format";
import { isReasonValid } from "./admin";
import { describeRefundError } from "./errors";

// Refund penuh untuk order tunai yang sudah lunas tapi belum dimasak.
export default function RefundPanel({ order, token, onBack, onDone, onUnauthorized }) {
  const total = Number(order.total);
  const [reason, setReason] = useState("");
  const [understood, setUnderstood] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const ready = isReasonValid(reason) && understood;

  async function onSubmit(e) {
    e.preventDefault();
    if (busy || !ready) return;
    setBusy(true);
    setError(null);
    try {
      const res = await refundPayment(token, order.payment_id, { amount: total, reason });
      setResult(res.data);
    } catch (err) {
      if (err?.status === 401) {
        onUnauthorized();
        return;
      }
      setError(describeRefundError(err));
      setBusy(false);
    }
  }

  if (result) {
    return (
      <>
        <section className="ticket" aria-live="polite">
          <p className="pill">Refund berhasil</p>
          <p className="ticket__number">{order.order_number}</p>
          <p className="muted ticket__name">{order.customer_name}</p>
        </section>
        <p className="muted pickup__meta">
          Kembalikan {formatRupiah(result.refunded_amount)} tunai ke customer. Order dibatalkan dan
          stok sudah dikembalikan.
        </p>
        <button type="button" className="btn btn--block" onClick={onDone}>
          Selesai
        </button>
      </>
    );
  }

  return (
    <>
      <button type="button" className="link-btn" onClick={onBack}>
        ← Kembali
      </button>
      <h1 className="page-title">Refund · {order.order_number}</h1>

      <section className="surface summary" aria-label="Rincian refund">
        <div className="summary__row">
          <span>Atas nama</span>
          <span>{order.customer_name}</span>
        </div>
        <div className="summary__row summary__row--total">
          <span>Dikembalikan</span>
          <strong>{formatRupiah(total)}</strong>
        </div>
      </section>

      <div className="notice refund__warning" role="note">
        <p className="notice__title">Yang akan terjadi</p>
        <p className="muted">
          Uang tunai dikembalikan ke customer secara manual. Order dibatalkan dan stok dikembalikan.
          Refund tidak bisa dibatalkan.
        </p>
      </div>

      <form onSubmit={onSubmit} noValidate>
        {error && (
          <div className="alert" role="alert">
            <p className="alert__title">{error}</p>
          </div>
        )}
        <div className="field">
          <label className="field__label" htmlFor="refund-reason">
            Alasan refund
          </label>
          <textarea
            id="refund-reason"
            className="input input--area"
            maxLength={500}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </div>
        <label className="refund__confirm">
          <input type="checkbox" checked={understood} onChange={(e) => setUnderstood(e.target.checked)} />
          <span>Saya paham refund ini tidak bisa dibatalkan.</span>
        </label>
        <div className="row-actions">
          <button type="button" className="btn btn--ghost" disabled={busy} onClick={onBack}>
            Batal
          </button>
          <button type="submit" className="btn" disabled={!ready || busy}>
            {busy ? "Memproses…" : `Refund ${formatRupiah(total)}`}
          </button>
        </div>
      </form>
    </>
  );
}
