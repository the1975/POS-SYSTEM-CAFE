import { Navigate } from "react-router-dom";
import BottomBar from "../components/layout/BottomBar";
import Header from "../components/layout/Header";
import { useCheckout } from "../features/checkout/useCheckout";
import { useCart } from "../stores/CartContext";
import { formatRupiah } from "../utils/format";

function Svg({ children }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {children}
    </svg>
  );
}

// Pilihan cara bayar: kartu dengan ikon dan tanda centang. Input radio tetap ada (tersembunyi) untuk aksesibilitas.
function Option({ value, title, hint, checked, disabled, onChange, icon }) {
  return (
    <label className={`option${disabled ? " option--disabled" : ""}`}>
      <input type="radio" name="method" value={value} checked={checked} disabled={disabled} onChange={onChange} />
      <span className="option__icon"><Svg>{icon}</Svg></span>
      <span className="option__text">
        <strong>{title}</strong>
        <span className="muted">{hint}</span>
      </span>
      <span className="option__check"><Svg><path d="M5 12l5 5 9-10" /></Svg></span>
    </label>
  );
}

export default function CheckoutPage() {
  const { subtotal } = useCart();
  const c = useCheckout();

  // Keranjang kosong (mis. halaman dibuka langsung): tidak ada yang dipesan.
  if (c.items.length === 0 && !c.submitting) return <Navigate to="/keranjang" replace />;

  return (
    <>
      <Header backTo="/keranjang" />
      <main className="container has-bar">
        <h1 className="page-title">Checkout</h1>

        {c.error && (
          <div className="alert" role="alert">
            <p className="alert__title">{c.error.title}</p>
            <p className="muted">{c.error.message}</p>
            {c.error.unavailable && (
              <>
                <ul className="alert__list">
                  {c.error.unavailable.map((i) => (
                    <li key={i.productId}>{i.name}</li>
                  ))}
                </ul>
                <button type="button" className="btn btn--sm" onClick={c.removeUnavailable}>
                  Hapus dari keranjang
                </button>
              </>
            )}
          </div>
        )}

        <section className="field">
          <label className="field__label" htmlFor="customer-name">
            Nama pemesan
          </label>
          <input
            id="customer-name"
            className="input"
            value={c.name}
            maxLength={100}
            autoComplete="name"
            autoCapitalize="words"
            placeholder="Nama kamu"
            aria-invalid={Boolean(c.nameError)}
            aria-describedby={c.nameError ? "customer-name-help" : undefined}
            onChange={(e) => c.setName(e.target.value)}
          />
          {c.nameError && (
            <p id="customer-name-help" className="field__error">
              {c.nameError}
            </p>
          )}
        </section>

        <fieldset className="field">
          <legend className="field__label">Cara bayar</legend>
          <Option
            value="CASH"
            title="Tunai"
            hint="Bayar di kasir"
            checked={c.method === "CASH"}
            onChange={() => c.setMethod("CASH")}
            icon={<><rect x="2" y="6" width="20" height="12" rx="2" /><circle cx="12" cy="12" r="2.5" /></>}
          />
          {/* QRIS belum aktif: pembayarannya dibangun di tahap Payments. */}
          <Option
            value="QRIS"
            title="QRIS"
            hint="Segera hadir"
            disabled
            icon={<><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><path d="M14 14h3v3M21 14v7h-4" /></>}
          />
        </fieldset>

        <section className="summary surface" aria-label="Ringkasan pesanan">
          {c.items.map((i) => (
            <div key={i.productId} className="summary__row summary__row--item">
              <span>
                {i.quantity} × {i.name}
              </span>
              <span>{formatRupiah(i.price * i.quantity)}</span>
            </div>
          ))}
          <div className="summary__row summary__row--total">
            <span>Subtotal</span>
            <strong>{formatRupiah(subtotal)}</strong>
          </div>
          <p className="muted summary__note">Pajak dihitung saat pesanan dibuat.</p>
        </section>
      </main>
      <BottomBar
        label="Subtotal"
        value={formatRupiah(subtotal)}
        actionLabel="Buat pesanan"
        onAction={c.submit}
        loading={c.submitting}
      />
    </>
  );
}
