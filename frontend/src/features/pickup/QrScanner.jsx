import { useEffect, useRef, useState } from "react";

export default function QrScanner({ onDetected, onCancel }) {
  const videoRef = useRef(null);
  const detectedRef = useRef(onDetected);
  detectedRef.current = onDetected;
  const [error, setError] = useState(null);

  useEffect(() => {
    let stream = null;
    let timer = null;
    let stopped = false;

    async function start() {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError("Kamera tidak tersedia di browser ini. Pakai kolom tempel token.");
        return;
      }
      try {
        const [{ default: jsQR }, media] = await Promise.all([
          import("jsqr"),
          navigator.mediaDevices.getUserMedia({
            video: { facingMode: { ideal: "environment" } },
            audio: false,
          }),
        ]);
        if (stopped) {
          media.getTracks().forEach((t) => t.stop());
          return;
        }
        stream = media;
        const video = videoRef.current;
        video.srcObject = stream;
        await video.play();

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d", { willReadFrequently: true });
        timer = setInterval(() => {
          if (video.readyState < 2 || !video.videoWidth) return;
          const scale = Math.min(1, 480 / video.videoWidth); // kecilkan: pemindaian lebih cepat
          canvas.width = Math.round(video.videoWidth * scale);
          canvas.height = Math.round(video.videoHeight * scale);
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const code = jsQR(img.data, img.width, img.height, { inversionAttempts: "dontInvert" });
          if (code?.data) {
            clearInterval(timer);
            timer = null;
            detectedRef.current(code.data);
          }
        }, 200);
      } catch (err) {
        if (stopped) return;
        setError(
          err?.name === "NotAllowedError"
            ? "Izin kamera ditolak. Izinkan kamera di browser, atau pakai kolom tempel token."
            : "Kamera tidak bisa dibuka. Pakai kolom tempel token."
        );
      }
    }

    start();
    return () => {
      stopped = true;
      clearInterval(timer);
      stream?.getTracks().forEach((t) => t.stop()); // matikan kamera saat layar ditutup
    };
  }, []);

  return (
    <div className="scanner">
      <h1 className="page-title">Scan QR pickup</h1>
      {error ? (
        <div className="alert" role="alert">
          <p className="alert__title">{error}</p>
        </div>
      ) : (
        <>
          <video ref={videoRef} className="scanner__video" playsInline muted />
          <p className="muted">Arahkan kamera ke QR di HP customer.</p>
        </>
      )}
      <button type="button" className="btn btn--ghost btn--block" onClick={onCancel}>
        Batal
      </button>
    </div>
  );
}
