import { useEffect, useState } from "react";
import { ApiError } from "../../services/api";
import { getOrder } from "../../services/orderApi";

export const POLL_MS = 5000;
const FINAL_STATUSES = ["COMPLETED", "CANCELLED"];
export const isFinalStatus = (status) => FINAL_STATUSES.includes(status);

// Memuat satu pesanan dengan token dari perangkat ini, lalu memperbaruinya tiap beberapa detik
// sampai pesanan selesai/dibatalkan (polling: cara resmi untuk MVP, lihat api-design.md).
export function useOrder(orderId, token, { intervalMs = POLL_MS } = {}) {
  const [state, setState] = useState({ status: token ? "loading" : "notfound", order: null });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!token) {
      setState({ status: "notfound", order: null });
      return undefined;
    }
    let cancelled = false;
    let timer = null;
    let hasOrder = false;
    const controller = new AbortController();

    function schedule() {
      timer = setTimeout(() => {
        if (document.visibilityState === "visible") load();
        else schedule(); // tab tersembunyi: tunda, jangan membebani server
      }, intervalMs);
    }

    async function load() {
      try {
        const res = await getOrder(orderId, token, { signal: controller.signal });
        if (cancelled) return;
        hasOrder = true;
        setState({ status: "ready", order: res.data });
        if (!isFinalStatus(res.data.status)) schedule();
      } catch (err) {
        if (cancelled || err?.name === "AbortError") return;
        if (err instanceof ApiError && err.status === 404) {
          setState({ status: "notfound", order: null });
          return;
        }
        if (hasOrder) {
          schedule(); // gagal memperbarui: data lama tetap tampil, coba lagi nanti
        } else {
          setState({ status: "error", order: null });
        }
      }
    }

    setState((s) => ({ ...s, status: "loading" }));
    load();
    return () => {
      cancelled = true;
      clearTimeout(timer);
      controller.abort();
    };
  }, [orderId, token, intervalMs, reloadKey]);

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}
