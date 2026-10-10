// Chip kategori. Dibuat wrap (bukan scroll samping) agar semua pilihan langsung terlihat.
export default function CategoryTabs({ categories, activeId, onSelect }) {
  if (categories.length === 0) return null;
  const options = [{ id: null, name: "Semua" }, ...categories];
  return (
    <nav className="chips" aria-label="Kategori menu">
      {options.map((c) => (
        <button
          key={c.id ?? "all"}
          type="button"
          className="chip"
          aria-pressed={activeId === c.id}
          onClick={() => onSelect(c.id)}
        >
          {c.name}
        </button>
      ))}
    </nav>
  );
}
