import { useState } from "react";
import BottomBar from "../../components/layout/BottomBar";
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
  const short = cash > 0 && !enough;

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
    <div className="cashpanel">
      <div className="cashhead">
        <button type="button" className="header__back" aria-label="Kembali" onClick={onBack}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M15 6l-6 6 6 6" />
          </svg>
        </button>
        <span className="orow__no">{order.order_number}</span>
        <span className="queue__name">{order.customer_name}</span>
      </div>

      <section className="surface cashtotal" aria-label="Rincian pembayaran">
        <span className="cashtotal__label">Total</span>
        <strong className="cashtotal__value">{formatRupiah(total)}</strong>
      </section>

      <div className="field">
        <label className="field__label" htmlFor="cash-received">
          Uang diterima
        </label>
        <input
          id="cash-received"
          className="input cashinput"
          inputMode="numeric"
          autoComplete="off"
          placeholder="Rp0"
          value={cash ? formatRupiah(cash) : ""}
          onChange={(e) => setCash(parseRupiahInput(e.target.value))}
          aria-invalid={short}
        />
        <div className="qa">
          {quickAmounts(total).map((v) => (
            <button key={v} type="button" className="qa__btn" aria-pressed={cash === v} onClick={() => setCash(v)}>
              {v === Math.ceil(total) ? "Uang pas" : formatRupiah(v)}
            </button>
          ))}
        </div>
      </div>

      <div className={`cashchange${enough ? " cashchange--ok" : short ? " cashchange--short" : ""}`} role={short ? "alert" : undefined}>
        <span>{short ? "Kurang" : "Kembalian"}</span>
        <strong>{enough ? formatRupiah(changeFor(total, cash)) : short ? formatRupiah(total - cash) : "—"}</strong>
      </div>

      {error && (
        <div className="alert cash__alert" role="alert">
          <p className="alert__title">{error}</p>
        </div>
      )}

      <BottomBar actionLabel="Konfirmasi pembayaran" onAction={onConfirm} loading={busy} disabled={!enough} raised />
    </div>
  );
}
