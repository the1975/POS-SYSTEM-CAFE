import { useState } from "react";
import { ApiError } from "../../services/api";
import { cancelOrder } from "../../services/orderApi";
import { formatCountdown } from "./countdown";
import { useCountdown } from "./useCountdown";

// Batas bayar + tombol batalkan (dua langkah supaya tidak terpencet) untuk pesanan PENDING.
export default function CancelOrder({ orderId, token, order, onChanged }) {
  const left = useCountdown(order.expires_at);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleCancel() {
    setBusy(true);
    setError("");
    try {
      await cancelOrder(orderId, token);
      onChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Koneksi bermasalah. Coba lagi.");
      setConfirming(false);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="cancel" aria-label="Batas bayar dan pembatalan">
      {left !== null && (
        <p className="muted" role="timer">
          {left > 0
            ? `Selesaikan pembayaran dalam ${formatCountdown(left)}`
            : "Waktu bayar habis. Pesanan akan dibatalkan otomatis."}
        </p>
      )}
      {error && (
        <p className="field__error" role="alert">
          {error}
        </p>
      )}
      {!confirming ? (
        <button type="button" className="btn btn--ghost btn--danger btn--block" onClick={() => setConfirming(true)}>
          Batalkan pesanan
        </button>
      ) : (
        <>
          <p className="notice__title">Yakin batalkan pesanan?</p>
          <div className="row-actions">
            <button type="button" className="btn btn--ghost" onClick={() => setConfirming(false)} disabled={busy}>
              Tidak
            </button>
            <button type="button" className="btn btn--solid-danger" onClick={handleCancel} disabled={busy}>
              {busy ? "Membatalkan…" : "Ya, batalkan"}
            </button>
          </div>
        </>
      )}
    </section>
  );
}
