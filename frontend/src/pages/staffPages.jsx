import AdminPage from "./AdminPage";
import CashierPage from "./CashierPage";
import KitchenPage from "./KitchenPage";
import PickupPage from "./PickupPage";
import StaffScreenPage from "./StaffScreenPage";

// Layar yang sudah jadi didaftarkan di sini; sisanya memakai kerangka "segera hadir".
const PAGES = { "/admin": AdminPage, "/kasir": CashierPage, "/dapur": KitchenPage, "/pickup": PickupPage };

export function renderStaffScreen(screen) {
  const Page = PAGES[screen.path] ?? StaffScreenPage;
  return <Page screen={screen} />;
}
