import { useState } from "react";
import { confirmCash } from "../../services/staffApi";
import { formatRupiah } from "../../utils/format";
import { changeFor, parseRupiahInput, quickAmounts } from "./cash";
import { describeCashError } from "./errors";

export default function CashPaymentPanel({ order, token, onBack, onDone, onUnauthorized }) {
  const total = Number(order.total);
  const [cash, setCash] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const enough = cash >= total;

  async function onConfirm() {
    if (busy || !enough) return;
    setBusy(true);
    setError(null);
    try {
      const res = await confirmCash(token, order.payment_id, cash);
      setResult(res.data);
    } catch (err) {
      if (err?.status === 401) {
        onUnauthorized();
        return;
      }
      setError(describeCashError(err));
      setBusy(false);
    }
  }

  if (result) {
    return (
      <>
        <section className="ticket" aria-live="polite">
          <p className="pill">Pembayaran diterima</p>
          <p className="muted">Kembalian</p>
          <p className="change">{formatRupiah(result.change)}</p>
          <p className="muted ticket__name">
            {order.order_number} · {order.customer_name}
          </p>
        </section>
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
      <h1 className="page-title">Bayar tunai · {order.order_number}</h1>

      <section className="surface summary" aria-label="Rincian pembayaran">
        <div className="summary__row">
          <span>Atas nama</span>
          <span>{order.customer_name}</span>
        </div>
        <div className="summary__row summary__row--total">
          <span>Total</span>
          <strong>{formatRupiah(total)}</strong>
        </div>
      </section>

      <div className="field cash__field">
        <label className="field__label" htmlFor="cash-received">
          Uang diterima
        </label>
        <input
          id="cash-received"
          className="input"
          inputMode="numeric"
          autoComplete="off"
          placeholder="Rp0"
          value={cash ? formatRupiah(cash) : ""}
          onChange={(e) => setCash(parseRupiahInput(e.target.value))}
          aria-invalid={cash > 0 && !enough}
        />
        <div className="chips">
          {quickAmounts(total).map((v) => (
            <button
              key={v}
              type="button"
              className="chip"
              aria-pressed={cash === v}
              onClick={() => setCash(v)}
            >
              {v === Math.ceil(total) ? "Uang pas" : formatRupiah(v)}
            </button>
          ))}
        </div>
        {cash > 0 && !enough && (
          <p className="field__error" role="alert">
            Uang belum mencukupi.
          </p>
        )}
      </div>

      <div className="summary__row summary__row--total">
        <span>Kembalian</span>
        <strong>{enough ? formatRupiah(changeFor(total, cash)) : "—"}</strong>
      </div>

      {error && (
        <div className="alert cash__alert" role="alert">
          <p className="alert__title">{error}</p>
        </div>
      )}

      <button
        type="button"
        className="btn btn--block"
        disabled={!enough || busy}
        onClick={onConfirm}
      >
        {busy ? "Memproses…" : "Konfirmasi pembayaran"}
      </button>
    </>
  );
}
