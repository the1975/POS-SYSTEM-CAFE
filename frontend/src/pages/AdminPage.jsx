import { useState } from "react";
import StaffHeader from "../components/layout/StaffHeader";
import Fab from "../components/ui/Fab";
import { ADMIN_TABS } from "../features/admin/admin";
import AdminNav from "../features/admin/AdminNav";
import AdminOrders from "../features/admin/AdminOrders";
import AdminDashboard from "../features/admin/AdminDashboard";
import AdminProducts from "../features/admin/AdminProducts";
import AdminStock from "../features/admin/AdminStock";
import AdminUsers from "../features/admin/AdminUsers";
import CreateUserPanel from "../features/admin/CreateUserPanel";
import EditUserPanel from "../features/admin/EditUserPanel";
import ProductFormPanel from "../features/admin/ProductFormPanel";
import StockAdjustPanel from "../features/admin/StockAdjustPanel";
import RefundPanel from "../features/admin/RefundPanel";
import { useCategories } from "../features/admin/useAdminProducts";
import { useRoles } from "../features/admin/useUsers";
import { useAuth } from "../stores/AuthContext";

// Layar Admin. Tab Order (+ refund), Produk, dan Pengguna sudah punya backend; tab lain "segera".
export default function AdminPage({ screen }) {
  const { user, token, logout } = useAuth();
  const { roles } = useRoles(token, logout);
  const { categories } = useCategories();
  const [tab, setTab] = useState("dashboard");
  const [orderFilters, setOrderFilters] = useState({ status: "", paymentStatus: "", search: "", page: 1 });
  const [userFilters, setUserFilters] = useState({ roleId: "", isActive: "", search: "", page: 1 });
  const [refunding, setRefunding] = useState(null);
  const [userPanel, setUserPanel] = useState(null); // { mode: "create" } | { mode: "edit", user }
  const [productFilters, setProductFilters] = useState({ categoryId: "", isAvailable: "", search: "", page: 1 });
  const [productPanel, setProductPanel] = useState(null); // { product: null } = tambah | { product } = ubah
  const [stockFilters, setStockFilters] = useState({ categoryId: "", search: "", page: 1 });
  const [stockItem, setStockItem] = useState(null); // item stok yang sedang diatur

  function renderBody() {
    if (refunding) {
      return (
        <RefundPanel
          key={refunding.order_id}
          order={refunding}
          token={token}
          onBack={() => setRefunding(null)}
          onDone={() => setRefunding(null)}
          onUnauthorized={logout}
        />
      );
    }
    if (userPanel?.mode === "create") {
      return (
        <CreateUserPanel
          token={token}
          roles={roles}
          onBack={() => setUserPanel(null)}
          onDone={() => setUserPanel(null)}
          onUnauthorized={logout}
        />
      );
    }
    if (userPanel?.mode === "edit") {
      return (
        <EditUserPanel
          key={userPanel.user.id}
          token={token}
          user={userPanel.user}
          roles={roles}
          isSelf={userPanel.user.id === user.id}
          onBack={() => setUserPanel(null)}
          onDone={() => setUserPanel(null)}
          onUnauthorized={logout}
        />
      );
    }
    if (stockItem) {
      return (
        <StockAdjustPanel
          key={stockItem.product_id}
          token={token}
          item={stockItem}
          onBack={() => setStockItem(null)}
          onDone={() => setStockItem(null)}
          onUnauthorized={logout}
        />
      );
    }
    if (productPanel) {
      return (
        <ProductFormPanel
          key={productPanel.product?.id ?? "new"}
          token={token}
          product={productPanel.product}
          categories={categories}
          onBack={() => setProductPanel(null)}
          onDone={() => setProductPanel(null)}
          onUnauthorized={logout}
        />
      );
    }
    return (
      <>
        <AdminNav tabs={ADMIN_TABS} current={tab} onSelect={setTab} />
        {tab === "orders" ? (
          <>
            <h1 className="page-title">Order</h1>
            <AdminOrders
              token={token}
              filters={orderFilters}
              onFilters={setOrderFilters}
              onRefund={setRefunding}
              onUnauthorized={logout}
            />
          </>
        ) : tab === "dashboard" ? (
          <>
            <h1 className="page-title">Dashboard</h1>
            <AdminDashboard token={token} onUnauthorized={logout} />
          </>
        ) : tab === "inventory" ? (
          <>
            <div className="admin__top">
              <h1 className="page-title">Stok</h1>
            </div>
            <AdminStock
              token={token}
              categories={categories}
              filters={stockFilters}
              onFilters={setStockFilters}
              onAdjust={setStockItem}
              onUnauthorized={logout}
            />
          </>
        ) : tab === "products" ? (
          <>
            <h1 className="page-title">Produk</h1>
            <Fab label="Tambah produk" onClick={() => setProductPanel({ product: null })} />
            <AdminProducts
              token={token}
              categories={categories}
              filters={productFilters}
              onFilters={setProductFilters}
              onEdit={(p) => setProductPanel({ product: p })}
              onUnauthorized={logout}
            />
          </>
        ) : (
          <>
            <h1 className="page-title">Pengguna</h1>
            <Fab label="Tambah pengguna" onClick={() => setUserPanel({ mode: "create" })} />
            <AdminUsers
              token={token}
              me={user.id}
              roles={roles}
              filters={userFilters}
              onFilters={setUserFilters}
              onEdit={(u) => setUserPanel({ mode: "edit", user: u })}
              onUnauthorized={logout}
            />
          </>
        )}
      </>
    );
  }

  return (
    <>
      <StaffHeader title={screen.title} user={user} onLogout={logout} />
      <main className="container has-nav">{renderBody()}</main>
    </>
  );
}
