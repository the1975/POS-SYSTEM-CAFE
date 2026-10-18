import { useCallback, useEffect, useState } from "react";
import { listKitchenOrders } from "../../services/staffApi";
import { mergeOrder } from "./kitchen";

// status: loading | ready | stale (gagal memperbarui, data lama tetap tampil) | error
export function useKitchenQueue(token, { intervalMs = 4000, onUnauthorized } = {}) {
  const [state, setState] = useState({ status: "loading", orders: [] });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();

    async function load() {
      try {
        const res = await listKitchenOrders(token, { signal: controller.signal });
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
  }, [token, reloadKey]);

  // Hasil aksi (order terbaru dari server) langsung dipakai, tanpa menunggu polling berikutnya.
  const applyUpdate = useCallback(
    (order) => setState((s) => ({ ...s, orders: mergeOrder(s.orders, order) })),
    []
  );

  return { ...state, applyUpdate, reload: () => setReloadKey((k) => k + 1) };
}
