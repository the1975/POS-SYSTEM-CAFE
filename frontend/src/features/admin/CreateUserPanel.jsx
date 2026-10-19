import { useState } from "react";
import { createUser } from "../../services/staffApi";
import {
  MIN_PASSWORD_LENGTH,
  describeUserError,
  generatePassword,
  isCreateFormValid,
  roleLabel,
} from "./users";

export default function CreateUserPanel({ token, roles, onBack, onDone, onUnauthorized }) {
  const [form, setForm] = useState({ name: "", email: "", roleId: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [created, setCreated] = useState(null); // { user, password }
  const [copied, setCopied] = useState(false);
  const ready = isCreateFormValid(form);
  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  function generate() {
    setForm((f) => ({ ...f, password: generatePassword() }));
    setShowPassword(true);
  }

  async function onSubmit(e) {
    e.preventDefault();
    if (busy || !ready) return;
    setBusy(true);
    setError(null);
    try {
      const res = await createUser(token, form);
      setCreated({ user: res.data, password: form.password });
    } catch (err) {
      if (err?.status === 401) {
        onUnauthorized();
        return;
      }
      setError(describeUserError(err));
      setBusy(false);
    }
  }

  async function copyPassword() {
    try {
      await navigator.clipboard.writeText(created.password);
      setCopied(true);
    } catch {
      /* browser menolak: sandi tetap terlihat, bisa disalin manual */
    }
  }

  if (created) {
    return (
      <>
        <section className="ticket" aria-live="polite">
          <p className="pill">Akun dibuat</p>
          <p className="ticket__number users__created">{created.user.name}</p>
          <p className="muted ticket__name">
            {created.user.email} · {roleLabel(created.user.role)}
          </p>
        </section>
        <div className="notice">
          <p className="notice__title">Sandi akun</p>
          <code className="secret">{created.password}</code>
          <button type="button" className="btn btn--sm btn--ghost users__copy" onClick={copyPassword}>
            {copied ? "Tersalin" : "Salin sandi"}
          </button>
          <p className="muted">Berikan ke stafnya sekarang. Sandi ini tidak akan ditampilkan lagi.</p>
        </div>
        <button type="button" className="btn btn--block" onClick={onDone}>
          Selesai
        </button>
      </>
    );
  }

  return (
    <>
      <button type="button" className="link-btn" onClick={onBack}>
        ← Kembali
      </button>
      <h1 className="page-title">Tambah akun</h1>

      <form onSubmit={onSubmit} noValidate>
        {error && (
          <div className="alert" role="alert">
            <p className="alert__title">{error}</p>
          </div>
        )}
        <div className="field">
          <label className="field__label" htmlFor="user-name">
            Nama
          </label>
          <input id="user-name" className="input" maxLength={100} value={form.name} onChange={set("name")} />
        </div>
        <div className="field">
          <label className="field__label" htmlFor="user-email">
            Email
          </label>
          <input
            id="user-email"
            className="input"
            type="email"
            inputMode="email"
            autoCapitalize="none"
            autoComplete="off"
            value={form.email}
            onChange={set("email")}
          />
        </div>
        <div className="field">
          <label className="field__label" htmlFor="user-role">
            Role
          </label>
          <select id="user-role" className="input" value={form.roleId} onChange={set("roleId")}>
            <option value="">Pilih role…</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {roleLabel(r.name)}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="field__label" htmlFor="user-password">
            Sandi (minimal {MIN_PASSWORD_LENGTH} karakter)
          </label>
          <input
            id="user-password"
            className="input"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            autoCapitalize="none"
            spellCheck={false}
            maxLength={200}
            value={form.password}
            onChange={set("password")}
          />
          <div className="pwline">
            <button type="button" className="btn btn--sm btn--ghost" onClick={generate}>
              Buat sandi acak
            </button>
            <label className="check">
              <input type="checkbox" checked={showPassword} onChange={(e) => setShowPassword(e.target.checked)} />
              <span>Tampilkan sandi</span>
            </label>
          </div>
        </div>
        <div className="row-actions">
          <button type="button" className="btn btn--ghost" disabled={busy} onClick={onBack}>
            Batal
          </button>
          <button type="submit" className="btn" disabled={!ready || busy}>
            {busy ? "Memproses…" : "Buat akun"}
          </button>
        </div>
      </form>
    </>
  );
}
