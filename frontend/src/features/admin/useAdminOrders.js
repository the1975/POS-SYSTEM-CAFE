import { useEffect, useState } from "react";
import { listStaffOrders } from "../../services/staffApi";

export const ADMIN_PAGE_SIZE = 20;

// status: loading | ready | stale (gagal memperbarui, data lama tetap tampil) | error
export function useAdminOrders(
  token,
  { status, paymentStatus, search, page },
  { intervalMs = 10000, onUnauthorized } = {}
) {
  const key = [status, paymentStatus, search, page].join("|");
  const [state, setState] = useState({ key, status: "loading", orders: [], pagination: null });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    // Filter/halaman berganti: kosongkan daftar lama supaya tidak menyesatkan.
    setState((s) => (s.key === key ? s : { key, status: "loading", orders: [], pagination: null }));

    async function load() {
      try {
        const res = await listStaffOrders(token, {
          status: status || undefined,
          paymentStatus: paymentStatus || undefined,
          search: search || undefined,
          page,
          pageSize: ADMIN_PAGE_SIZE,
          signal: controller.signal,
        });
        if (!cancelled) {
          setState({ key, status: "ready", orders: res.data, pagination: res.pagination });
        }
      } catch (err) {
        if (cancelled || err?.name === "AbortError") return;
        if (err?.status === 401) {
          onUnauthorized?.();
          return;
        }
        setState((s) => ({ ...s, status: s.orders.length ? "stale" : "error" }));
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
  }, [token, key, reloadKey]);

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}
