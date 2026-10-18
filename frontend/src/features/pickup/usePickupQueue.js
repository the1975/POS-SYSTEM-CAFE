import { useEffect, useState } from "react";
import { listPickupOrders } from "../../services/staffApi";
import { PICKUP_STATUSES, sortByReadyAt } from "./pickup";

// status: loading | ready | stale (gagal memperbarui, data lama tetap tampil) | error
export function usePickupQueue(token, { intervalMs = 5000, onUnauthorized } = {}) {
  const [state, setState] = useState({ status: "loading", orders: [] });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();

    async function load() {
      try {
        const results = await Promise.all(
          PICKUP_STATUSES.map((s) => listPickupOrders(token, s, { signal: controller.signal }))
        );
        if (!cancelled) {
          setState({ status: "ready", orders: sortByReadyAt(results.flatMap((r) => r.data)) });
        }
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

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}
