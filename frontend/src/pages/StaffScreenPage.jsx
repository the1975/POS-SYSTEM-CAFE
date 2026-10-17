import { Link } from "react-router-dom";
import { EmptyState } from "../components/feedback/States";
import StaffHeader from "../components/layout/StaffHeader";
import { screensForRole } from "../features/staff/screens";
import { useAuth } from "../stores/AuthContext";

// Kerangka layar staff. Isi layar sebenarnya menggantikan EmptyState ini satu per satu.
export default function StaffScreenPage({ screen }) {
  const { user, logout } = useAuth();
  const others = screensForRole(user.role).filter((s) => s.path !== screen.path);
  return (
    <>
      <StaffHeader title={screen.title} user={user} onLogout={logout} />
      <main className="container">
        {others.length > 0 && (
          <nav className="staff-nav" aria-label="Pindah layar">
            {others.map((s) => (
              <Link key={s.path} to={s.path} className="chip">
                {s.title}
              </Link>
            ))}
          </nav>
        )}
        <EmptyState title={`Layar ${screen.title} segera hadir.`} hint={screen.hint} />
      </main>
    </>
  );
}
