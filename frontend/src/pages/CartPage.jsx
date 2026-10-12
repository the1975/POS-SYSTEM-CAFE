import { Link } from "react-router-dom";
import BottomBar from "../components/layout/BottomBar";
import Header from "../components/layout/Header";
import QuantityStepper from "../components/ui/QuantityStepper";
import { useCart } from "../stores/CartContext";
import { formatRupiah } from "../utils/format";

export default function CartPage() {
  const { items, count, subtotal, setQuantity, remove } = useCart();

  if (items.length === 0) {
    return (
      <>
        <Header title="Keranjang" backTo="/" />
        <main className="container">
          <div className="state">
            <h1 className="state__title">Keranjangmu masih kosong.</h1>
            <p className="muted">Pilih menu yang kamu suka, nanti muncul di sini.</p>
            <Link to="/" className="btn">
              Lihat menu
            </Link>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Header title="Keranjang" backTo="/" />
      <main className="container has-bar">
        <h1 className="page-title">Pesananmu</h1>
        <ul className="list surface">
          {items.map((item) => (
            <li key={item.productId} className="line">
              <div>
                <h2 className="line__name">{item.name}</h2>
                <p className="muted">{formatRupiah(item.price)}</p>
              </div>
              <p className="line__total">{formatRupiah(item.price * item.quantity)}</p>
              <div className="line__actions">
                <QuantityStepper
                  value={item.quantity}
                  label={item.name}
                  onChange={(q) => setQuantity(item.productId, q)}
                />
                <button type="button" className="link-btn" onClick={() => remove(item.productId)}>
                  Hapus
                </button>
              </div>
            </li>
          ))}
        </ul>

        <section className="summary surface" aria-label="Ringkasan">
          <div className="summary__row">
            <span>Subtotal ({count} item)</span>
            <strong>{formatRupiah(subtotal)}</strong>
          </div>
          {/* Jujur soal angka: total akhir dihitung server dari harga terbaru di database. */}
          <p className="muted summary__note">
            Pajak dan total akhir dihitung otomatis saat pesanan dibuat.
          </p>
        </section>
      </main>
      <BottomBar
        label="Subtotal"
        value={formatRupiah(subtotal)}
        actionLabel="Lanjut ke pemesanan"
        to="/pemesanan"
      />
    </>
  );
}
