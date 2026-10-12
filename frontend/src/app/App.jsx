import { Route, Routes } from "react-router-dom";
import CartPage from "../pages/CartPage";
import MenuPage from "../pages/MenuPage";
import NotFoundPage from "../pages/NotFoundPage";

// Alur customer: Menu -> Keranjang -> Pemesanan -> Status (dua terakhir menyusul).
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MenuPage />} />
      <Route path="/keranjang" element={<CartPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
