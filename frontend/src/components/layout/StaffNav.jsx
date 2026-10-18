import { Link } from "react-router-dom";
import { screensForRole } from "../../features/staff/screens";

export default function StaffNav({ role, current }) {
  const others = screensForRole(role).filter((s) => s.path !== current);
  if (others.length === 0) return null;
  return (
    <nav className="staff-nav" aria-label="Pindah layar">
      {others.map((s) => (
        <Link key={s.path} to={s.path} className="chip">
          {s.title}
        </Link>
      ))}
    </nav>
  );
}
