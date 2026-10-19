import { useEffect, useState } from "react";
import { EmptyState } from "../../components/feedback/States";
import { pageInfo } from "./admin";
import { USER_STATUS_FILTERS, roleLabel } from "./users";
import { useUsers } from "./useUsers";

export default function AdminUsers({ token, me, roles, filters, onFilters, onEdit, onUnauthorized }) {
  const { status, users, pagination, reload } = useUsers(token, filters, { onUnauthorized });
  const [draft, setDraft] = useState(filters.search);
  const info = pageInfo(pagination, "akun");
  const change = (patch) => onFilters({ ...filters, ...patch, page: 1 });

  useEffect(() => {
    if (pagination && pagination.total_pages > 0 && filters.page > pagination.total_pages) {
      onFilters({ ...filters, page: pagination.total_pages });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination]);

  return (
    <>
      <form
        className="searchbar"
        role="search"
        onSubmit={(e) => {
          e.preventDefault();
          change({ search: draft.trim() });
        }}
      >
        <input
          className="input"
          type="search"
          aria-label="Cari nama atau email"
          placeholder="Nama atau email"
          maxLength={100}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <button type="submit" className="btn btn--sm">
          Cari
        </button>
      </form>

      <div className="admin__filters">
        <select
          className="input"
          aria-label="Filter role"
          value={filters.roleId}
          onChange={(e) => change({ roleId: e.target.value })}
        >
          <option value="">Semua role</option>
          {roles.map((r) => (
            <option key={r.id} value={r.id}>
              {roleLabel(r.name)}
            </option>
          ))}
        </select>
        <select
          className="input"
          aria-label="Filter status akun"
          value={filters.isActive}
          onChange={(e) => change({ isActive: e.target.value })}
        >
          {USER_STATUS_FILTERS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      {status === "loading" && <p className="muted state">Memuat akun…</p>}
      {status === "error" && (
        <div className="state" role="alert">
          <h2 className="state__title">Akun belum bisa dimuat.</h2>
          <p className="muted">Periksa koneksi, lalu coba lagi.</p>
          <button type="button" className="btn" onClick={reload}>
            Coba lagi
          </button>
        </div>
      )}
      {status === "ready" && users.length === 0 && (
        <EmptyState title="Tidak ada akun." hint="Coba ubah filter atau kata pencarian." />
      )}

      {users.length > 0 && (
        <ul className="list surface">
          {users.map((u) => (
            <li key={u.id} className="queue__row">
              <span className="queue__main">
                <span className="queue__name">
                  {u.name}
                  {u.id === me ? " (kamu)" : ""}
                </span>
                <span className="muted users__email">{u.email}</span>
                <span className="admin__chips">
                  <span className="pill">{roleLabel(u.role)}</span>
                  {!u.is_active && <span className="pill pill--warn">Nonaktif</span>}
                </span>
              </span>
              <button type="button" className="btn btn--sm btn--ghost" onClick={() => onEdit(u)}>
                Ubah
              </button>
            </li>
          ))}
        </ul>
      )}

      {info.label && (
        <div className="admin__pager">
          <button
            type="button"
            className="btn btn--sm btn--ghost"
            disabled={!info.hasPrev}
            onClick={() => onFilters({ ...filters, page: filters.page - 1 })}
          >
            Sebelumnya
          </button>
          <span className="muted">{info.label}</span>
          <button
            type="button"
            className="btn btn--sm btn--ghost"
            disabled={!info.hasNext}
            onClick={() => onFilters({ ...filters, page: filters.page + 1 })}
          >
            Berikutnya
          </button>
        </div>
      )}
    </>
  );
}
