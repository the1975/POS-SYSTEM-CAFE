import { Link, useLocation } from "react-router-dom";
import { screensForRole } from "../../features/staff/screens";

const ICONS = {
  "/kasir": (
    <>
      <rect x="2" y="6" width="20" height="12" rx="2" />
      <circle cx="12" cy="12" r="2.5" />
    </>
  ),
  "/dapur": <path d="M4 11h16v2a6 6 0 0 1-6 6h-4a6 6 0 0 1-6-6v-2zM8 7c0-1 1-1 1-3M12 7c0-1 1-1 1-3M16 7c0-1 1-1 1-3" />,
  "/pickup": <path d="M6 7h12l1 13H5zM9 7a3 3 0 0 1 6 0" />,
  "/admin": <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />,
};

// Navbar bawah untuk staf yang boleh membuka lebih dari satu layar (mis. Kasir + Pickup).
export default function StaffNav({ role }) {
  const { pathname } = useLocation();
  const screens = screensForRole(role);
  if (screens.length < 2) return null;
  return (
    <nav className="catnav catnav--fit" aria-label="Layar staf">
      <div className="catnav__brand" aria-hidden="true">
        <span className="catnav__logo">M</span>
        <b>Monster Café</b>
      </div>
      {screens.map((s) => (
        <Link key={s.path} to={s.path} className="catnav__item" aria-current={pathname === s.path ? "page" : undefined}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            {ICONS[s.path]}
          </svg>
          {s.title}
        </Link>
      ))}
    </nav>
  );
}
