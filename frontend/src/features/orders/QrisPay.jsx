import { useEffect, useState } from "react";
import { ApiError } from "../../services/api";
import { createQris } from "../../services/paymentApi";
import { formatRupiah } from "../../utils/format";
import PickupQr from "./PickupQr";
import { saveQrImage } from "./qrImage";

// Tagihan QRIS untuk pesanan PENDING. Memanggil backend sekali saat tampil (aman diulang).
export default function QrisPay({ orderId, token, total }) {
  const [state, setState] = useState({ status: "loading", data: null, message: "" });
  const [tryKey, setTryKey] = useState(0);
  const [saveNote, setSaveNote] = useState("");

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading", data: null, message: "" });
    createQris(orderId, token)
      .then((res) => {
        if (!cancelled) setState({ status: "ready", data: res.data, message: "" });
      })
      .catch((err) => {
        if (cancelled) return;
        const message = err instanceof ApiError ? err.message : "Koneksi bermasalah.";
        setState({ status: "error", data: null, message });
      });
    return () => {
      cancelled = true;
    };
  }, [orderId, token, tryKey]);

  async function handleSave() {
    setSaveNote("");
    try {
      await saveQrImage(state.data.payment_url, "qris-pembayaran.png");
      setSaveNote("QR tersimpan. Buka e-wallet, pilih Scan, lalu pilih gambar dari galeri atau unduhan.");
    } catch {
      setSaveNote("QR belum bisa disimpan. Coba lagi.");
    }
  }

  const isMock = state.data?.payment_url?.includes("mock-pay.invalid");

  return (
    <section className="notice pickup" aria-label="Pembayaran QRIS">
      <p className="notice__title">Bayar dengan QRIS</p>
      {state.status === "loading" && <span className="pickup__qr skeleton" aria-hidden="true" />}
      {state.status === "error" && (
        <>
          <p className="field__error" role="alert">
            {state.message}
          </p>
          <button type="button" className="btn btn--ghost" onClick={() => setTryKey((k) => k + 1)}>
            Coba lagi
          </button>
        </>
      )}
      {state.status === "ready" && (
        <>
          <PickupQr token={state.data.payment_url} alt="QR pembayaran QRIS" />
          <p className="muted">Pindai dengan e-wallet atau m-banking, lalu bayar {formatRupiah(total)}.</p>
          <button type="button" className="btn btn--ghost" onClick={handleSave}>
            Simpan QR
          </button>
          {saveNote && (
            <p className="muted" role="status">
              {saveNote}
            </p>
          )}
          {isMock && <p className="muted">Mode uji coba: QR ini belum bisa dibayar sungguhan.</p>}
        </>
      )}
    </section>
  );
}
