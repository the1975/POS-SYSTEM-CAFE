import BottomBar from "../../components/layout/BottomBar";
import { useCart } from "../../stores/CartContext";
import { formatRupiah } from "../../utils/format";

// Muncul di halaman menu begitu ada isi keranjang (cart visibility).
export default function CartBar({ raised }) {
  const { count, subtotal } = useCart();
  if (count === 0) return null;
  return (
    <BottomBar
      raised={raised}
      label={`${count} item`}
      value={formatRupiah(subtotal)}
      actionLabel="Lihat keranjang"
      to="/keranjang"
    />
  );
}
