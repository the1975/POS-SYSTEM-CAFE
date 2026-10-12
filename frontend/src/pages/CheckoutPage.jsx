import { Navigate } from "react-router-dom";
import BottomBar from "../components/layout/BottomBar";
import Header from "../components/layout/Header";
import { useCheckout } from "../features/checkout/useCheckout";
import { useCart } from "../stores/CartContext";
import { formatRupiah } from "../utils/format";

export default function CheckoutPage() {
  const { subtotal } = useCart();
  const c = useCheckout();

  // Keranjang kosong (mis. halaman dibuka langsung): tidak ada yang dipesan.
  if (c.items.length === 0 && !c.submitting) return <Navigate to="/keranjang" replace />;

  return (
    <>
      <Header title="Pemesanan" backTo="/keranjang" />
      <main className="container has-bar">
        <h1 className="page-title">Satu langkah lagi</h1>

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
            aria-invalid={Boolean(c.nameError)}
            aria-describedby="customer-name-help"
            onChange={(e) => c.setName(e.target.value)}
          />
          <p id="customer-name-help" className={c.nameError ? "field__error" : "muted"}>
            {c.nameError ?? "Dipakai untuk memanggil pesananmu."}
          </p>
        </section>

        <fieldset className="field">
          <legend className="field__label">Cara bayar</legend>
          <label className="option">
            <input
              type="radio"
              name="method"
              value="CASH"
              checked={c.method === "CASH"}
              onChange={() => c.setMethod("CASH")}
            />
            <span>
              <strong>Tunai di kasir</strong>
              <span className="muted">Bayar di kasir dulu, lalu pesananmu diproses.</span>
            </span>
          </label>
          {/* QRIS belum aktif: pembayarannya dibangun di tahap Payments. */}
          <label className="option option--disabled">
            <input type="radio" name="method" value="QRIS" disabled />
            <span>
              <strong>QRIS</strong>
              <span className="muted">Segera hadir.</span>
            </span>
          </label>
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
          <p className="muted summary__note">
            Pajak dan total akhir dihitung otomatis saat pesanan dibuat.
          </p>
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
