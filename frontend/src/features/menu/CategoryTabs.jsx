// Selector kategori: navbar bawah (ikon + label). Ikon dipilih dari nama kategori.
const ICONS = {
  all: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="2" />
      <rect x="14" y="3" width="7" height="7" rx="2" />
      <rect x="3" y="14" width="7" height="7" rx="2" />
      <rect x="14" y="14" width="7" height="7" rx="2" />
    </>
  ),
  drink: (
    <>
      <path d="M5 8h11v6a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4V8z" />
      <path d="M16 10h1.5a2.5 2.5 0 0 1 0 5H16M8 3v2M12 3v2" />
    </>
  ),
  food: <path d="M7 3v8M4 3v5a3 3 0 0 0 6 0V3M7 11v10M17 3c-2 2-3 5-3 8h3v10" />,
  snack: (
    <>
      <circle cx="12" cy="12" r="9" />
      <circle cx="9" cy="10" r=".8" fill="currentColor" />
      <circle cx="14" cy="9" r=".8" fill="currentColor" />
      <circle cx="13" cy="14" r=".8" fill="currentColor" />
    </>
  ),
  other: <path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8zM7.5 7.5h.01" />,
};

function iconFor(name) {
  const n = name.toLowerCase();
  if (/minum|drink|kopi|teh|jus/.test(n)) return "drink";
  if (/makan|food|nasi|main/.test(n)) return "food";
  if (/camil|snack|kue|dessert/.test(n)) return "snack";
  return "other";
}

function Icon({ kind }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {ICONS[kind]}
    </svg>
  );
}

export default function CategoryTabs({ categories, activeId, onSelect }) {
  if (categories.length === 0) return null;
  const options = [{ id: null, name: "Semua" }, ...categories];
  return (
    <nav className="catnav" aria-label="Kategori menu">
      <div className="catnav__brand" aria-hidden="true">
        <span className="catnav__logo">M</span>
        <b>Monster Café</b>
      </div>
      {options.map((c) => (
        <button
          key={c.id ?? "all"}
          type="button"
          className="catnav__item"
          aria-pressed={activeId === c.id}
          onClick={() => onSelect(c.id)}
        >
          <Icon kind={c.id === null ? "all" : iconFor(c.name)} />
          {c.name}
        </button>
      ))}
    </nav>
  );
}
