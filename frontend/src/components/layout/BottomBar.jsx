import { Link } from "react-router-dom";

// Bar aksi melayang di bawah layar. Kaca (glass) dipakai HANYA di sini sebagai aksen,
// karena ini satu-satunya elemen yang melayang di atas konten.
export default function BottomBar({ label, value, actionLabel, to }) {
  return (
    <div className="bar">
      <div className="bar__inner">
        <div>
          <p className="bar__label">{label}</p>
          <p className="bar__value">{value}</p>
        </div>
        <Link to={to} className="btn">
          {actionLabel}
        </Link>
      </div>
    </div>
  );
}
