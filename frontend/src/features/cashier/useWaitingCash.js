import { useEffect, useState } from "react";
import { listStaffOrders } from "../../services/staffApi";

// status: loading | ready | stale (gagal memperbarui, data lama tetap tampil) | error
export function useWaitingCash(token, search, { intervalMs = 5000, onUnauthorized } = {}) {
  const [state, setState] = useState({ status: "loading", orders: [] });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();

    async function load() {
      try {
        const res = await listStaffOrders(token, {
          paymentStatus: "WAITING_CASH",
          search: search || undefined,
          signal: controller.signal,
        });
        if (!cancelled) setState({ status: "ready", orders: res.data });
      } catch (err) {
        if (cancelled || err?.name === "AbortError") return;
        if (err?.status === 401) {
          onUnauthorized?.();
          return;
        }
        setState((s) => ({ status: s.orders.length ? "stale" : "error", orders: s.orders }));
      }
    }

    setState((s) => ({ ...s, status: s.orders.length ? "ready" : "loading" }));
    load();
    const id = setInterval(() => {
      if (document.visibilityState === "visible") load();
    }, intervalMs);
    return () => {
      cancelled = true;
      controller.abort();
      clearInterval(id);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, search, reloadKey]);

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}
