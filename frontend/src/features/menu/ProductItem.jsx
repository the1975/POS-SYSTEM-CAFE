import { useState } from "react";
import QuantityStepper from "../../components/ui/QuantityStepper";
import { useCart } from "../../stores/CartContext";
import { formatRupiah } from "../../utils/format";

// Foto produk bersifat opsional. Kalau tidak ada / gagal dimuat, tampilkan huruf awal nama.
function Thumb({ name, imageUrl }) {
  const [broken, setBroken] = useState(false);
  if (!imageUrl || broken) {
    return (
      <span className="thumb thumb--empty" aria-hidden="true">
        {name.charAt(0).toUpperCase()}
      </span>
    );
  }
  return (
    <img className="thumb" src={imageUrl} alt="" loading="lazy" onError={() => setBroken(true)} />
  );
}

export default function ProductItem({ product }) {
  const { quantityOf, add, setQuantity } = useCart();
  const quantity = quantityOf(product.id);
  const soldOut = !product.in_stock;

  return (
    <li className={`item${soldOut ? " item--soldout" : ""}`}>
      <Thumb name={product.name} imageUrl={product.image_url} />
      <div className="item__body">
        <h3 className="item__name">{product.name}</h3>
        {product.description && <p className="item__desc">{product.description}</p>}
        <div className="item__meta">
          <span className="price">{formatRupiah(product.price)}</span>
          {soldOut ? (
            // Status stok memakai teks, bukan hanya warna.
            <span className="badge">Habis</span>
          ) : quantity === 0 ? (
            <button
              type="button"
              className="btn btn--sm"
              aria-label={`Tambah ${product.name} ke keranjang`}
              onClick={() => add(product)}
            >
              Tambah
            </button>
          ) : (
            <QuantityStepper
              value={quantity}
              label={product.name}
              onChange={(q) => setQuantity(product.id, q)}
            />
          )}
        </div>
      </div>
    </li>
  );
}
