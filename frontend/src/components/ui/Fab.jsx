// Tombol tambah melayang di kanan bawah (gaya WhatsApp), di atas navbar bawah.
export default function Fab({ label, onClick }) {
  return (
    <button type="button" className="fab" aria-label={label} onClick={onClick}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" aria-hidden="true">
        <path d="M12 5v14M5 12h14" />
      </svg>
    </button>
  );
}
