import { Navigate } from "react-router-dom";
import { EmptyState } from "../../components/feedback/States";
import { homeForRole } from "../../stores/auth";
import { useAuth } from "../../stores/AuthContext";

// Belum login -> halaman login. Role tidak cocok -> halaman awal role-nya sendiri.
export default function RequireRole({ roles, children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/staff/login" replace />;
  if (roles.includes(user.role)) return children;
  const home = homeForRole(user.role);
  if (home) return <Navigate to={home} replace />;
  return (
    <main className="container">
      <EmptyState title="Akun ini belum punya halaman." hint="Hubungi admin untuk mengatur role akunmu." />
    </main>
  );
}
