import { Link } from "react-router-dom";
import QuantityStepper from "../../components/ui/QuantityStepper";
import { useCart } from "../../stores/CartContext";
import { formatRupiah } from "../../utils/format";

// Panel keranjang di sisi kanan layar laptop (bar keranjang disembunyikan di layar itu).
export default function CartPanel() {
  const { items, count, subtotal, setQuantity } = useCart();
  return (
    <aside className="cartpanel" aria-label="Pesananmu">
      <h2 className="cartpanel__title">Pesananmu</h2>
      {items.length === 0 ? (
        <p className="muted">Belum ada pesanan.</p>
      ) : (
        <ul className="cartpanel__list">
          {items.map((i) => (
            <li key={i.productId} className="cartpanel__row">
              <span className="queue__main">
                <span className="queue__name">{i.name}</span>
                <span className="muted">{formatRupiah(i.price)}</span>
              </span>
              <QuantityStepper value={i.quantity} label={i.name} onChange={(q) => setQuantity(i.productId, q)} />
            </li>
          ))}
        </ul>
      )}
      <div className="cartpanel__foot">
        <div className="summary__row">
          <span>Subtotal · {count} item</span>
          <strong>{formatRupiah(subtotal)}</strong>
        </div>
        <p className="muted summary__note">Pajak dihitung saat pesanan dibuat.</p>
        {items.length > 0 ? (
          <Link to="/pemesanan" className="btn btn--block">
            Checkout
          </Link>
        ) : (
          <button type="button" className="btn btn--block" disabled>
            Checkout
          </button>
        )}
      </div>
    </aside>
  );
}
