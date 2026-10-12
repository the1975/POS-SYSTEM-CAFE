import { useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createOrder } from "../../services/orderApi";
import { saveOrderAccess } from "../../stores/orderAccess";
import { useCart } from "../../stores/CartContext";
import { newIdempotencyKey } from "../../utils/id";
import { describeCheckoutError } from "./errors";

// Seluruh logika pemesanan; komponen halaman hanya menampilkan.
export function useCheckout() {
  const { items, removeMany, clear } = useCart();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [method, setMethod] = useState("CASH");
  const [submitting, setSubmitting] = useState(false);
  const [nameError, setNameError] = useState(null);
  const [error, setError] = useState(null);

  const payload = useMemo(
    () => ({
      customerName: name.trim(),
      paymentMethod: method,
      items: items.map((i) => ({ product_id: i.productId, quantity: i.quantity })),
    }),
    [name, method, items]
  );

  // Aturan kunci: isi SAMA -> kunci SAMA (retry aman); isi BERBEDA -> kunci baru.
  // Backend menolak kunci yang sama untuk isi berbeda, jadi ini wajib.
  const attempt = useRef({ signature: "", key: "" });
  function keyFor(p) {
    const signature = JSON.stringify(p);
    if (attempt.current.signature !== signature) {
      attempt.current = { signature, key: newIdempotencyKey() };
    }
    return attempt.current.key;
  }

  async function submit() {
    if (submitting) return; // cegah klik ganda
    if (!payload.customerName) {
      setNameError("Nama wajib diisi agar pesananmu bisa dipanggil.");
      return;
    }
    setNameError(null);
    setError(null);
    setSubmitting(true);
    try {
      const { data: order } = await createOrder(payload, keyFor(payload));
      saveOrderAccess({
        orderId: order.order_id,
        orderNumber: order.order_number,
        token: order.tracking_token,
      });
      clear();
      navigate(`/pesanan/${order.order_id}`, { replace: true });
    } catch (err) {
      setError(describeCheckoutError(err, items));
      setSubmitting(false);
    }
  }

  function removeUnavailable() {
    if (error?.unavailable) removeMany(error.unavailable.map((i) => i.productId));
    setError(null);
  }

  return {
    items, name, setName, method, setMethod,
    submitting, nameError, error, submit, removeUnavailable,
  };
}
