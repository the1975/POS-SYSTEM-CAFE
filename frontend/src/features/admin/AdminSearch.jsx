import { useState } from "react";

// Kolom cari untuk daftar admin: Enter untuk mencari, dikosongkan = tampil semua lagi.
export default function AdminSearch({ label, placeholder, filters, onFilters }) {
  const [draft, setDraft] = useState(filters.search);
  const apply = (search) => onFilters({ ...filters, search, page: 1 });

  return (
    <form
      className="usearch"
      role="search"
      onSubmit={(e) => {
        e.preventDefault();
        apply(draft.trim());
      }}
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
        <circle cx="11" cy="11" r="7" />
        <path d="M20 20l-4-4" />
      </svg>
      <input
        className="usearch__input"
        type="search"
        aria-label={label}
        placeholder={placeholder}
        maxLength={100}
        value={draft}
        onChange={(e) => {
          setDraft(e.target.value);
          if (e.target.value === "" && filters.search !== "") apply("");
        }}
      />
    </form>
  );
}
