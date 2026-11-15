// Menu admin: navbar bawah (ikon + label), gayanya sama dengan navbar kategori customer.
const ICONS = {
  dashboard: <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />,
  orders: <path d="M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6" />,
  products: <path d="M21 8l-9-5-9 5v8l9 5 9-5zM3 8l9 5 9-5M12 13v8" />,
  inventory: <path d="M12 3l9 5-9 5-9-5zM3 13l9 5 9-5" />,
  users: (
    <>
      <circle cx="9" cy="8" r="4" />
      <path d="M2 21a7 7 0 0 1 14 0M17 4a4 4 0 0 1 0 8M22 21a7 7 0 0 0-4-6" />
    </>
  ),
};
const ORDER = ["dashboard", "orders", "products", "inventory", "users"];

export default function AdminNav({ tabs, current, onSelect }) {
  const sorted = ORDER.map((id) => tabs.find((t) => t.id === id)).filter(Boolean);
  return (
    <nav className="catnav catnav--fit" aria-label="Menu admin">
      {sorted.map((t) => (
        <button
          key={t.id}
          type="button"
          className="catnav__item"
          aria-pressed={current === t.id}
          disabled={!t.ready}
          onClick={() => onSelect(t.id)}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            {ICONS[t.id]}
          </svg>
          {t.label}
        </button>
      ))}
    </nav>
  );
}
