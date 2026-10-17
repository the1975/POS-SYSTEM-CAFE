import { Route, Routes } from "react-router-dom";
import CartPage from "../pages/CartPage";
import CheckoutPage from "../pages/CheckoutPage";
import MenuPage from "../pages/MenuPage";
import NotFoundPage from "../pages/NotFoundPage";
import OrderPage from "../pages/OrderPage";
import StaffLoginPage from "../pages/StaffLoginPage";
import StaffScreenPage from "../pages/StaffScreenPage";
import RequireRole from "../features/staff/RequireRole";
import { STAFF_SCREENS } from "../features/staff/screens";

// Alur customer: Menu -> Keranjang -> Pemesanan -> Status pesanan.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MenuPage />} />
      <Route path="/keranjang" element={<CartPage />} />
      <Route path="/pemesanan" element={<CheckoutPage />} />
      <Route path="/pesanan/:orderId" element={<OrderPage />} />
      <Route path="/staff/login" element={<StaffLoginPage />} />
      {STAFF_SCREENS.map((s) => (
        <Route
          key={s.path}
          path={s.path}
          element={
            <RequireRole roles={s.roles}>
              <StaffScreenPage screen={s} />
            </RequireRole>
          }
        />
      ))}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
