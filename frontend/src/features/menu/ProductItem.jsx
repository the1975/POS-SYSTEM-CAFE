import { useState } from "react";
import QuantityStepper from "../../components/ui/QuantityStepper";
import { useCart } from "../../stores/CartContext";
import { formatRupiah } from "../../utils/format";

// Foto produk bersifat opsional. Kalau tidak ada / gagal dimuat, tampilkan huruf awal nama.
function Thumb({ name, imageUrl }) {
  const [broken, setBroken] = useState(false);
  if (!imageUrl || broken) {
    return (
      <span className="pcard__thumb pcard__thumb--empty" aria-hidden="true">
        {name.charAt(0).toUpperCase()}
      </span>
    );
  }
  return (
    <img className="pcard__thumb" src={imageUrl} alt="" loading="lazy" onError={() => setBroken(true)} />
  );
}

// Kartu menu: foto, nama, harga, tombol tambah. Deskripsi tidak ditampilkan agar kartu tetap bersih.
export default function ProductItem({ product }) {
  const { quantityOf, add, setQuantity } = useCart();
  const quantity = quantityOf(product.id);
  const soldOut = !product.in_stock;

  return (
    <li className={`pcard${soldOut ? " pcard--soldout" : ""}`}>
      <Thumb name={product.name} imageUrl={product.image_url} />
      <h3 className="pcard__name">{product.name}</h3>
      <div className="pcard__meta">
        <span className="price">{formatRupiah(product.price)}</span>
        {soldOut ? (
          // Status stok memakai teks, bukan hanya warna.
          <span className="badge">Habis</span>
        ) : quantity === 0 ? (
          <button
            type="button"
            className="pcard__add"
            aria-label={`Tambah ${product.name} ke keranjang`}
            onClick={() => add(product)}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6"
              strokeLinecap="round" aria-hidden="true">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </button>
        ) : (
          <QuantityStepper
            value={quantity}
            label={product.name}
            onChange={(q) => setQuantity(product.id, q)}
          />
        )}
      </div>
    </li>
  );
}
