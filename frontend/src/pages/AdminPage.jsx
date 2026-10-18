import { useState } from "react";
import StaffHeader from "../components/layout/StaffHeader";
import StaffNav from "../components/layout/StaffNav";
import { ADMIN_TABS } from "../features/admin/admin";
import AdminOrders from "../features/admin/AdminOrders";
import RefundPanel from "../features/admin/RefundPanel";
import { useAuth } from "../stores/AuthContext";

// Layar Admin. Baru tab Order (+ refund) yang punya backend; tab lain "segera".
export default function AdminPage({ screen }) {
  const { user, token, logout } = useAuth();
  const [filters, setFilters] = useState({ status: "", paymentStatus: "", search: "", page: 1 });
  const [refunding, setRefunding] = useState(null);

  return (
    <>
      <StaffHeader title={screen.title} user={user} onLogout={logout} />
      <main className="container">
        {refunding ? (
          <RefundPanel
            key={refunding.order_id}
            order={refunding}
            token={token}
            onBack={() => setRefunding(null)}
            onDone={() => setRefunding(null)}
            onUnauthorized={logout}
          />
        ) : (
          <>
            <StaffNav role={user.role} current={screen.path} />
            <nav className="admin__tabs" aria-label="Menu admin">
              {ADMIN_TABS.map((t) =>
                t.ready ? (
                  <button key={t.id} type="button" className="chip" aria-pressed="true">
                    {t.label}
                  </button>
                ) : (
                  <button key={t.id} type="button" className="chip" disabled>
                    {t.label} · segera
                  </button>
                )
              )}
            </nav>
            <h1 className="page-title">Order</h1>
            <AdminOrders
              token={token}
              filters={filters}
              onFilters={setFilters}
              onRefund={setRefunding}
              onUnauthorized={logout}
            />
          </>
        )}
      </main>
    </>
  );
}
