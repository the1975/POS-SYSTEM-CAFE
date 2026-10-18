import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { EmptyState } from "../components/feedback/States";
import Header from "../components/layout/Header";
import PickupQr from "../features/orders/PickupQr";
import { shouldShowPickupQr } from "../features/orders/pickupQr";
import { statusLabel } from "../features/orders/statusLabels";
import { useOrder } from "../features/orders/useOrder";
import { getOrderAccess } from "../stores/orderAccess";
import { formatRupiah } from "../utils/format";

// Halaman status/konfirmasi pesanan. Nomor pesanan = momen utama halaman ini.
export default function OrderPage() {
  const { orderId } = useParams();
  const access = useMemo(() => getOrderAccess(orderId), [orderId]);
  const { status, order, reload } = useOrder(orderId, access?.token);

  return (
    <>
      <Header title="Pesanan" />
      <main className="container">
        {status === "loading" && <p className="muted state">Memuat pesananmu…</p>}

        {status === "notfound" && (
          <EmptyState
            title="Pesanan tidak ditemukan di perangkat ini."
            hint="Buka dari perangkat yang tadi dipakai memesan, atau tanyakan ke kasir."
          />
        )}

        {status === "error" && (
          <div className="state" role="alert">
            <h1 className="state__title">Pesanan belum bisa dimuat.</h1>
            <p className="muted">Pesananmu aman. Periksa koneksi, lalu coba lagi.</p>
            <button type="button" className="btn" onClick={reload}>
              Coba lagi
            </button>
          </div>
        )}

        {status === "ready" && (
          <>
            <section className="ticket" aria-label="Nomor pesanan">
              <p className="muted">Nomor pesananmu</p>
              <p className="ticket__number">{order.order_number}</p>
              <p className="pill">{statusLabel(order.status)}</p>
              <p className="muted ticket__name">Atas nama {order.customer_name}</p>
            </section>

            {shouldShowPickupQr(order) && (
              <section className="notice pickup" aria-label="QR pengambilan pesanan">
                <p className="notice__title">Ambil pesananmu</p>
                <PickupQr token={order.pickup_token} />
                <p className="muted">Tunjukkan QR ini ke petugas. Jangan dibagikan ke orang lain.</p>
              </section>
            )}

            {order.status === "PENDING" && order.payment_method === "CASH" && (
              <section className="notice">
                <p className="notice__title">Bayar di kasir</p>
                <p className="muted">
                  Sebutkan nomor {order.order_number} dan bayar {formatRupiah(order.total)}. Pesananmu
                  mulai diproses setelah pembayaran diterima.
                </p>
              </section>
            )}

            <ul className="list surface">
              {order.items.map((item, i) => (
                <li key={i} className="line line--simple">
                  <span>{item.name}</span>
                  <span className="muted">× {item.quantity}</span>
                </li>
              ))}
            </ul>

            <section className="summary surface" aria-label="Rincian pembayaran">
              <div className="summary__row summary__row--item">
                <span>Subtotal</span>
                <span>{formatRupiah(order.subtotal)}</span>
              </div>
              {order.discount_amount > 0 && (
                <div className="summary__row summary__row--item">
                  <span>Diskon</span>
                  <span>−{formatRupiah(order.discount_amount)}</span>
                </div>
              )}
              <div className="summary__row summary__row--item">
                <span>Pajak</span>
                <span>{formatRupiah(order.tax_amount)}</span>
              </div>
              <div className="summary__row summary__row--total">
                <span>Total</span>
                <strong>{formatRupiah(order.total)}</strong>
              </div>
            </section>

            <Link to="/" className="btn btn--ghost btn--block">
              Pesan lagi
            </Link>
          </>
        )}
      </main>
    </>
  );
}
