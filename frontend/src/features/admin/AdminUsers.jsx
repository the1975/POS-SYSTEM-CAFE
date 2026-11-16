import { useEffect, useState } from "react";
import { EmptyState } from "../../components/feedback/States";
import { pageInfo } from "./admin";
import { groupUsersByRole } from "./users";
import { useUsers } from "./useUsers";

// Daftar pengguna: dikelompokkan per role (tanpa filter), cukup cari nama atau email.
export default function AdminUsers({ token, me, filters, onFilters, onEdit, onUnauthorized }) {
  const { status, users, pagination, reload } = useUsers(token, filters, { onUnauthorized });
  const [draft, setDraft] = useState(filters.search);
  const info = pageInfo(pagination, "akun");
  const change = (patch) => onFilters({ ...filters, ...patch, page: 1 });
  const groups = groupUsersByRole(users);

  useEffect(() => {
    if (pagination && pagination.total_pages > 0 && filters.page > pagination.total_pages) {
      onFilters({ ...filters, page: pagination.total_pages });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination]);

  return (
    <>
      <form
        className="usearch"
        role="search"
        onSubmit={(e) => {
          e.preventDefault();
          change({ search: draft.trim() });
        }}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-4-4" />
        </svg>
        <input
          className="usearch__input"
          type="search"
          aria-label="Cari nama atau email"
          placeholder="Nama atau email"
          maxLength={100}
          value={draft}
          onChange={(e) => {
            setDraft(e.target.value);
            if (e.target.value === "" && filters.search !== "") change({ search: "" });
          }}
        />
      </form>

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
        <EmptyState title="Tidak ada akun." hint="Coba kata pencarian lain." />
      )}

      {groups.map((g) => (
        <section key={g.role} className="ugroup" aria-label={g.label}>
          <h2 className="ugroup__title">
            {g.label} · {g.items.length}
          </h2>
          <ul className="list surface ugroup__list">
            {g.items.map((u) => (
              <li key={u.id}>
                <button
                  type="button"
                  className={`urow${u.is_active ? "" : " urow--off"}`}
                  aria-label={`Ubah ${u.name}`}
                  onClick={() => onEdit(u)}
                >
                  <span className="urow__avatar" aria-hidden="true">
                    {u.name.charAt(0).toUpperCase()}
                  </span>
                  <span className="queue__main">
                    <span className="queue__name">
                      {u.name}
                      {u.id === me ? " (kamu)" : ""}
                    </span>
                    <span className="muted users__email">{u.email}</span>
                  </span>
                  {!u.is_active && <span className="pill pill--warn">Nonaktif</span>}
                  <svg className="urow__go" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M9 6l6 6-6 6" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        </section>
      ))}

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
