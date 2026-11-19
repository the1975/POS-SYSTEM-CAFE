import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { screensForRole } from "../../features/staff/screens";
import { ROLE_LABEL } from "../../stores/auth";
import Logo from "../ui/Logo";

// Header staf: judul layar + avatar. Avatar membuka menu akun (nama, role, pindah layar, keluar).
export default function StaffHeader({ title, user, onLogout }) {
  const [open, setOpen] = useState(false);
  const box = useRef(null);
  const { pathname } = useLocation();

  // Tutup menu saat klik di luar atau menekan Escape.
  useEffect(() => {
    if (!open) return undefined;
    const onDown = (e) => {
      if (box.current && !box.current.contains(e.target)) setOpen(false);
    };
    const onKey = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // Navbar bawah menangani pindah layar untuk staf; menu avatar hanya dipakai di layar Admin.
  const others = user && pathname.startsWith("/admin") ? screensForRole(user.role).filter((s) => s.path !== pathname) : [];

  return (
    <header className="header">
      <div className="container header__inner staff-bar">
        <span className="brand">
          <Logo />
          {title}
        </span>
        {user && (
          <div className="acct" ref={box}>
            <button
              type="button"
              className="acct__btn"
              aria-label="Menu akun"
              aria-haspopup="menu"
              aria-expanded={open}
              onClick={() => setOpen((v) => !v)}
            >
              {user.name.charAt(0).toUpperCase()}
            </button>
            {open && (
              <div className="acct__menu" role="menu">
                <div className="acct__who">
                  <strong>{user.name}</strong>
                  {user.email && <span className="muted acct__email">{user.email}</span>}
                  <span className="acct__role">{ROLE_LABEL[user.role] ?? user.role}</span>
                </div>
                {others.length > 0 && (
                  <>
                    <p className="acct__label">Pindah layar</p>
                    {others.map((s) => (
                      <Link key={s.path} to={s.path} role="menuitem" className="acct__item" onClick={() => setOpen(false)}>
                        {s.title}
                      </Link>
                    ))}
                  </>
                )}
                <button type="button" role="menuitem" className="acct__item acct__item--out" onClick={onLogout}>
                  Keluar
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
