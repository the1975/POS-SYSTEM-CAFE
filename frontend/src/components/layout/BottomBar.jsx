import { Link } from "react-router-dom";

const chevron = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M9 6l6 6-6 6" />
  </svg>
);

// Bar aksi melayang di bawah layar (hijau gradasi).
// Dengan `to` = tautan; dengan `onAction` = tombol (mis. kirim pesanan).
export default function BottomBar({ label, value, actionLabel, to, onAction, loading, disabled, raised }) {
  const solo = !label && !value; // tanpa teks ringkasan: hanya satu tombol selebar bar
  return (
    <div className={`bar${raised ? " bar--raised" : ""}`}>
      <div className={`bar__inner${solo ? " bar__inner--solo" : ""}`}>
        {!solo && (
          <div>
            <p className="bar__label">{label}</p>
            <p className="bar__value">{value}</p>
          </div>
        )}
        {to ? (
          <Link to={to} className="btn">
            {actionLabel}
            {chevron}
          </Link>
        ) : (
          <button type="button" className="btn" onClick={onAction} disabled={disabled || loading}>
            {loading ? "Memproses…" : <>{actionLabel}{chevron}</>}
          </button>
        )}
      </div>
    </div>
  );
}
