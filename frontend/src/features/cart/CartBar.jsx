import BottomBar from "../../components/layout/BottomBar";
import { useCart } from "../../stores/CartContext";
import { formatRupiah } from "../../utils/format";

// Muncul di halaman menu begitu ada isi keranjang (cart visibility).
export default function CartBar() {
  const { count, subtotal } = useCart();
  if (count === 0) return null;
  return (
    <BottomBar
      label={`${count} item di keranjang`}
      value={formatRupiah(subtotal)}
      actionLabel="Lihat keranjang"
      to="/keranjang"
    />
  );
}
