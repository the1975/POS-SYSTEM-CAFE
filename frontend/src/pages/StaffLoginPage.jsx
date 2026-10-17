import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import Header from "../components/layout/Header";
import { describeLoginError } from "../features/staff/errors";
import { homeForRole } from "../stores/auth";
import { useAuth } from "../stores/AuthContext";

export default function StaffLoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  // Sudah login: langsung ke halaman role-nya.
  if (user && homeForRole(user.role)) return <Navigate to={homeForRole(user.role)} replace />;

  async function onSubmit(e) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const session = await login(email.trim(), password);
      navigate(homeForRole(session.user.role) ?? "/staff/login", { replace: true });
    } catch (err) {
      setError(describeLoginError(err));
      setBusy(false);
    }
  }

  return (
    <>
      <Header title="Monster Café · Staff" />
      <main className="container">
        <h1 className="page-title">Masuk</h1>
        <form onSubmit={onSubmit} noValidate>
          {error && (
            <div className="alert" role="alert">
              <p className="alert__title">{error}</p>
            </div>
          )}
          <div className="field">
            <label className="field__label" htmlFor="staff-email">Email</label>
            <input
              id="staff-email"
              className="input"
              type="email"
              inputMode="email"
              autoComplete="username"
              autoCapitalize="none"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="field">
            <label className="field__label" htmlFor="staff-password">Kata sandi</label>
            <input
              id="staff-password"
              className="input"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn--block" disabled={busy || !email.trim() || !password}>
            {busy ? "Memeriksa…" : "Masuk"}
          </button>
        </form>
      </main>
    </>
  );
}
