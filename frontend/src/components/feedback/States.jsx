// Tiga keadaan yang wajib ada di setiap data asynchronous (design-system.md §42-44).

export function LoadingList({ rows = 6 }) {
  return (
    <div aria-busy="true" aria-live="polite">
      <p className="muted">Memuat menu…</p>
      <ul className="pgrid">
        {Array.from({ length: rows }, (_, i) => (
          <li key={i} className="pcard" aria-hidden="true">
            <span className="pcard__thumb skeleton" />
            <span className="skeleton skeleton--line" />
            <span className="skeleton skeleton--line skeleton--short" />
          </li>
        ))}
      </ul>
    </div>
  );
}

export function EmptyState({ title, hint, actionLabel, onAction }) {
  return (
    <div className="state" role="status">
      <h2 className="state__title">{title}</h2>
      <p className="muted">{hint}</p>
      {onAction && (
        <button type="button" className="btn" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export function ErrorState({ onRetry }) {
  // Menjelaskan apa yang terjadi, apakah data aman, dan apa yang bisa dilakukan.
  return (
    <div className="state" role="alert">
      <h2 className="state__title">Menu belum bisa dimuat.</h2>
      <p className="muted">
        Tidak ada data yang hilang. Periksa koneksi internet, lalu coba lagi.
      </p>
      <button type="button" className="btn" onClick={onRetry}>
        Coba lagi
      </button>
    </div>
  );
}
