import { Link } from "react-router-dom";
import Logo from "../ui/Logo";

// Tanpa backTo = header utama (logo + nama kafe). Dengan backTo = halaman dalam, ada tombol kembali bulat.
export default function Header({ title = "Monster Café", backTo }) {
  return (
    <header className="header">
      <div className="container header__inner">
        {backTo && (
          <Link to={backTo} className="header__back" aria-label="Kembali">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M15 6l-6 6 6 6" />
            </svg>
          </Link>
        )}
        <span className="brand">
          <Logo />
          {title}
        </span>
      </div>
    </header>
  );
}
