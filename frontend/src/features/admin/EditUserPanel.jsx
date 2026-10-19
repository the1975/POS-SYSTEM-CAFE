import { useState } from "react";
import { updateUser } from "../../services/staffApi";
import { buildUserPatch, describeUserError, roleLabel } from "./users";

export default function EditUserPanel({ token, user, roles, isSelf, onBack, onDone, onUnauthorized }) {
  const [form, setForm] = useState({ name: user.name, roleId: user.role_id, isActive: user.is_active });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(null);
  const patch = buildUserPatch(user, form);
  const changed = Object.keys(patch).length > 0;

  async function onSubmit(e) {
    e.preventDefault();
    if (busy || !changed) return;
    setBusy(true);
    setError(null);
    try {
      const res = await updateUser(token, user.id, patch);
      setSaved(res.data);
    } catch (err) {
      if (err?.status === 401) {
        onUnauthorized();
        return;
      }
      setError(describeUserError(err));
      setBusy(false);
    }
  }

  if (saved) {
    return (
      <>
        <section className="ticket" aria-live="polite">
          <p className="pill">Perubahan disimpan</p>
          <p className="ticket__number users__created">{saved.name}</p>
          <p className="muted ticket__name">
            {roleLabel(saved.role)} · {saved.is_active ? "Aktif" : "Nonaktif"}
          </p>
        </section>
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
      <h1 className="page-title">Ubah akun</h1>
      <p className="muted">{user.email}</p>

      <form onSubmit={onSubmit} noValidate>
        {error && (
          <div className="alert" role="alert">
            <p className="alert__title">{error}</p>
          </div>
        )}
        <div className="field">
          <label className="field__label" htmlFor="edit-name">
            Nama
          </label>
          <input
            id="edit-name"
            className="input"
            maxLength={100}
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          />
        </div>
        <div className="field">
          <label className="field__label" htmlFor="edit-role">
            Role
          </label>
          <select
            id="edit-role"
            className="input"
            value={form.roleId}
            disabled={isSelf}
            onChange={(e) => setForm((f) => ({ ...f, roleId: e.target.value }))}
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {roleLabel(r.name)}
              </option>
            ))}
          </select>
        </div>
        <label className="check">
          <input
            type="checkbox"
            checked={form.isActive}
            disabled={isSelf}
            onChange={(e) => setForm((f) => ({ ...f, isActive: e.target.checked }))}
          />
          <span>Akun aktif</span>
        </label>
        {isSelf && <p className="muted">Ini akunmu sendiri: role dan status tidak bisa diubah.</p>}
        {!form.isActive && (
          <p className="muted">Akun nonaktif langsung tidak bisa login, termasuk yang sedang masuk.</p>
        )}
        <div className="row-actions">
          <button type="button" className="btn btn--ghost" disabled={busy} onClick={onBack}>
            Batal
          </button>
          <button type="submit" className="btn" disabled={!changed || busy}>
            {busy ? "Menyimpan…" : "Simpan"}
          </button>
        </div>
      </form>
    </>
  );
}
