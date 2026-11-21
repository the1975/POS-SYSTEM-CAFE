import { Link } from "react-router-dom";
import BottomBar from "../components/layout/BottomBar";
import Header from "../components/layout/Header";
import QuantityStepper from "../components/ui/QuantityStepper";
import { useCart } from "../stores/CartContext";
import { formatRupiah } from "../utils/format";

export default function CartPage() {
  const { items, count, subtotal, setQuantity } = useCart();

  if (items.length === 0) {
    return (
      <>
        <Header title="Keranjang" backTo="/" />
        <main className="container">
          <div className="state">
            <h1 className="state__title">Keranjangmu masih kosong.</h1>
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
      <Header backTo="/" />
      <main className="container has-bar">
        <h1 className="page-title">Keranjang</h1>
        {/* Kurangi sampai 0 = item terhapus, jadi tidak perlu tombol hapus terpisah. */}
        <ul className="list surface">
          {items.map((item) => (
            <li key={item.productId} className="cline">
              <span className="cline__tile" aria-hidden="true">
                {item.name.charAt(0).toUpperCase()}
              </span>
              <div className="cline__body">
                <h2 className="line__name">{item.name}</h2>
                <p className="muted">{formatRupiah(item.price)}</p>
              </div>
              <QuantityStepper
                value={item.quantity}
                label={item.name}
                onChange={(q) => setQuantity(item.productId, q)}
              />
            </li>
          ))}
        </ul>

        <section className="summary surface" aria-label="Ringkasan">
          <div className="summary__row">
            <span>Subtotal</span>
            <strong>{formatRupiah(subtotal)}</strong>
          </div>
          {/* Jujur soal angka: total akhir dihitung server dari harga terbaru di database. */}
        </section>
      </main>
      <BottomBar
        label={`${count} item`}
        value={formatRupiah(subtotal)}
        actionLabel="Checkout"
        to="/pemesanan"
      />
    </>
  );
}
