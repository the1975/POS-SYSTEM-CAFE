import { useMemo } from "react";
import { Link } from "react-router-dom";
import { getLatestOrderAccess } from "../../stores/orderAccess";
import { statusLabel } from "./statusLabels";
import { isFinalStatus, useOrder } from "./useOrder";

// Jalan pulang ke pesanan yang masih berjalan, kalau halaman pesanan tertutup tanpa sengaja.
// Hanya pesanan terbaru di perangkat ini; hilang sendiri setelah selesai atau dibatalkan.
export default function ActiveOrderCard() {
  const access = useMemo(() => getLatestOrderAccess(), []);
  const { status, order } = useOrder(access?.orderId, access?.token);
  if (!access || status !== "ready" || isFinalStatus(order.status)) return null;

  return (
    <Link to={`/pesanan/${access.orderId}`} className="activeorder">
      <span className="orow__no">{order.order_number}</span>
      <span className="queue__main">
        <span className="queue__name">Pesananmu sedang berjalan</span>
        <span className="muted">{statusLabel(order.status)}</span>
      </span>
      <svg className="urow__go" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M9 6l6 6-6 6" />
      </svg>
    </Link>
  );
}
