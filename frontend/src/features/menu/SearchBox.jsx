export default function SearchBox({ value, onChange }) {
  return (
    <div className="search">
      {/* Label disembunyikan secara visual tapi tetap terbaca screen reader. */}
      <label htmlFor="menu-search" className="sr-only">
        Cari menu
      </label>
      <input
        id="menu-search"
        type="search"
        className="search__input"
        placeholder="Cari menu…"
        value={value}
        maxLength={100}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
