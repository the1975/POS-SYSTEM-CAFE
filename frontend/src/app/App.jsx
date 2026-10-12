import { Route, Routes } from "react-router-dom";
import CartPage from "../pages/CartPage";
import CheckoutPage from "../pages/CheckoutPage";
import MenuPage from "../pages/MenuPage";
import NotFoundPage from "../pages/NotFoundPage";
import OrderPage from "../pages/OrderPage";

// Alur customer: Menu -> Keranjang -> Pemesanan -> Status pesanan.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MenuPage />} />
      <Route path="/keranjang" element={<CartPage />} />
      <Route path="/pemesanan" element={<CheckoutPage />} />
      <Route path="/pesanan/:orderId" element={<OrderPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
