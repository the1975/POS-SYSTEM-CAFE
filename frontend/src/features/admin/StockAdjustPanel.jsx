import { useState } from "react";
import { adjustStock } from "../../services/staffApi";
import {
  MAX_REASON,
  STOCK_ACTIONS,
  actionById,
  buildAdjustBody,
  describeStockError,
  isAdjustValid,
  stockAfter,
} from "./stock";

export default function StockAdjustPanel({ token, item, onBack, onDone, onUnauthorized }) {
  const [actionId, setActionId] = useState("add");
  const [qty, setQty] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(null);

  const current = item.quantity_available;
  const after = stockAfter(current, actionId, qty);
  const ready = isAdjustValid(current, actionId, qty, reason);
  const action = actionById(actionId);

  async function onSubmit(e) {
    e.preventDefault();
    if (busy || !ready) return;
    setBusy(true);
    setError(null);
    try {
      const res = await adjustStock(token, item.product_id, buildAdjustBody(actionId, qty, reason));
      setSaved(res.data);
    } catch (err) {
      if (err?.status === 401) {
        onUnauthorized();
        return;
      }
      setError(describeStockError(err));
      setBusy(false);
    }
  }

  if (saved) {
    return (
      <>
        <section className="ticket" aria-live="polite">
          <p className="pill">Stok diperbarui</p>
          <p className="ticket__number users__created">{saved.product_name}</p>
          <p className="muted ticket__name">
            {current} → {saved.quantity_available}
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
      <h1 className="page-title">Atur stok</h1>
      <p className="muted">
        {item.product_name} · tersedia {current}
        {item.quantity_reserved > 0 ? ` · ditahan pesanan ${item.quantity_reserved} (tidak ikut berubah)` : ""}
      </p>

      <form onSubmit={onSubmit} noValidate>
        {error && (
          <div className="alert" role="alert">
            <p className="alert__title">{error}</p>
          </div>
        )}
        <div className="field">
          <label className="field__label" htmlFor="stock-action">
            Jenis
          </label>
          <select id="stock-action" className="input" value={actionId} onChange={(e) => setActionId(e.target.value)}>
            {STOCK_ACTIONS.map((a) => (
              <option key={a.id} value={a.id}>
                {a.label}
              </option>
            ))}
          </select>
          <p className="muted">{action.hint}</p>
        </div>
        <div className="field">
          <label className="field__label" htmlFor="stock-qty">
            Jumlah
          </label>
          <input
            id="stock-qty"
            className="input"
            inputMode="numeric"
            autoComplete="off"
            placeholder="10"
            value={qty}
            onChange={(e) => setQty(e.target.value)}
          />
          {after !== null && (
            <p className="muted" aria-live="polite">
              {after < 0 ? `Stok tidak cukup: ${current} dikurangi ${qty} jadi minus.` : `${current} → ${after}`}
            </p>
          )}
        </div>
        <div className="field">
          <label className="field__label" htmlFor="stock-reason">
            Alasan
          </label>
          <input
            id="stock-reason"
            className="input"
            maxLength={MAX_REASON}
            placeholder="Contoh: belanja pasar pagi"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </div>
        <div className="row-actions">
          <button type="button" className="btn btn--ghost" disabled={busy} onClick={onBack}>
            Batal
          </button>
          <button type="submit" className="btn" disabled={!ready || busy}>
            {busy ? "Menyimpan…" : "Simpan"}
          </button>
        </div>
      </form>
    </>
  );
}
