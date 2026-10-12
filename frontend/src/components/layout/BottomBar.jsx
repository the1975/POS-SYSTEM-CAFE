import { Link } from "react-router-dom";

// Bar aksi melayang di bawah layar. Kaca (glass) dipakai HANYA di sini sebagai aksen.
// Dengan `to` = tautan; dengan `onAction` = tombol (mis. kirim pesanan).
export default function BottomBar({ label, value, actionLabel, to, onAction, loading, disabled }) {
  return (
    <div className="bar">
      <div className="bar__inner">
        <div>
          <p className="bar__label">{label}</p>
          <p className="bar__value">{value}</p>
        </div>
        {to ? (
          <Link to={to} className="btn">
            {actionLabel}
          </Link>
        ) : (
          <button type="button" className="btn" onClick={onAction} disabled={disabled || loading}>
            {loading ? "Memproses…" : actionLabel}
          </button>
        )}
      </div>
    </div>
  );
}
