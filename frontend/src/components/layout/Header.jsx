import { Link } from "react-router-dom";

// Tanpa backTo = header utama (nama kafe). Dengan backTo = halaman dalam, ada tombol kembali.
export default function Header({ title = "Monster Café", backTo }) {
  return (
    <header className="header">
      <div className="container header__inner">
        {backTo && (
          <Link to={backTo} className="header__back" aria-label="Kembali">
            ←
          </Link>
        )}
        <span className="brand">{title}</span>
      </div>
    </header>
  );
}
