import CashierPage from "./CashierPage";
import StaffScreenPage from "./StaffScreenPage";

// Layar yang sudah jadi didaftarkan di sini; sisanya memakai kerangka "segera hadir".
const PAGES = { "/kasir": CashierPage };

export function renderStaffScreen(screen) {
  const Page = PAGES[screen.path] ?? StaffScreenPage;
  return <Page screen={screen} />;
}
