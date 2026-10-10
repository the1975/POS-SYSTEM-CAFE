import { useState } from "react";
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
    <img
      className="thumb"
      src={imageUrl}
      alt=""
      loading="lazy"
      onError={() => setBroken(true)}
    />
  );
}

export default function ProductItem({ product }) {
  const soldOut = !product.in_stock;
  return (
    <li className={`item${soldOut ? " item--soldout" : ""}`}>
      <Thumb name={product.name} imageUrl={product.image_url} />
      <div className="item__body">
        <h3 className="item__name">{product.name}</h3>
        {product.description && <p className="item__desc">{product.description}</p>}
        <p className="item__meta">
          <span className="price">{formatRupiah(product.price)}</span>
          {/* Status stok memakai teks, bukan hanya warna (design-system.md §5). */}
          {soldOut && <span className="badge">Habis</span>}
        </p>
      </div>
      {/* Tombol "+ Tambah" menyusul di tahap Cart (butuh state keranjang). */}
    </li>
  );
}
