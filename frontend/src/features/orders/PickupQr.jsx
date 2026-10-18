import { useEffect, useState } from "react";

// Token tidak ditampilkan sebagai teks: hanya dalam bentuk QR untuk dipindai petugas.
export default function PickupQr({ token }) {
  const [src, setSrc] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setSrc(null);
    setFailed(false);
    import("qrcode")
      .then(({ default: QRCode }) =>
        QRCode.toDataURL(token, {
          width: 320,
          margin: 2,
          errorCorrectionLevel: "M",
          color: { dark: "#000000", light: "#ffffff" }, // selalu hitam di putih, juga di mode gelap
        })
      )
      .then((url) => {
        if (!cancelled) setSrc(url);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (failed) return <p className="muted">QR belum bisa ditampilkan. Muat ulang halaman ini.</p>;
  if (!src) return <span className="pickup__qr skeleton" aria-hidden="true" />;
  return (
    <img className="pickup__qr" src={src} width="320" height="320" alt="QR pengambilan pesanan" />
  );
}
