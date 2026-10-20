import { useState } from "react";
import StaffHeader from "../components/layout/StaffHeader";
import StaffNav from "../components/layout/StaffNav";
import { ADMIN_TABS } from "../features/admin/admin";
import AdminOrders from "../features/admin/AdminOrders";
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
  const [tab, setTab] = useState("orders");
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
        <StaffNav role={user.role} current={screen.path} />
        <nav className="admin__tabs" aria-label="Menu admin">
          {ADMIN_TABS.map((t) =>
            t.ready ? (
              <button
                key={t.id}
                type="button"
                className="chip"
                aria-pressed={tab === t.id}
                onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ) : (
              <button key={t.id} type="button" className="chip" disabled>
                {t.label} · segera
              </button>
            )
          )}
        </nav>
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
            <div className="admin__top">
              <h1 className="page-title">Produk</h1>
              <button type="button" className="btn btn--sm" onClick={() => setProductPanel({ product: null })}>
                + Tambah
              </button>
            </div>
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
            <div className="admin__top">
              <h1 className="page-title">Pengguna</h1>
              <button type="button" className="btn btn--sm" onClick={() => setUserPanel({ mode: "create" })}>
                + Tambah
              </button>
            </div>
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
      <main className="container">{renderBody()}</main>
    </>
  );
}
