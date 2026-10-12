import { useEffect, useState } from "react";
import { ApiError } from "../../services/api";
import { getOrder } from "../../services/orderApi";

// Memuat satu pesanan dengan token dari perangkat ini. (Pembaruan otomatis menyusul di tahap tracking.)
export function useOrder(orderId, token) {
  const [state, setState] = useState({ status: token ? "loading" : "notfound", order: null });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!token) {
      setState({ status: "notfound", order: null });
      return undefined;
    }
    const controller = new AbortController();
    setState((s) => ({ ...s, status: "loading" }));
    getOrder(orderId, token, { signal: controller.signal })
      .then((res) => setState({ status: "ready", order: res.data }))
      .catch((err) => {
        if (err.name === "AbortError") return;
        const notFound = err instanceof ApiError && err.status === 404;
        setState({ status: notFound ? "notfound" : "error", order: null });
      });
    return () => controller.abort();
  }, [orderId, token, reloadKey]);

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}
