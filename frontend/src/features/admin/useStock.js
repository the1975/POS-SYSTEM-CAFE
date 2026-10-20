import { useEffect, useState } from "react";
import { listStock } from "../../services/staffApi";
import { STOCK_PAGE_SIZE } from "./stock";

// status: loading | ready | error. Tanpa polling: stok dikoreksi manual oleh admin.
export function useStock(token, { categoryId, search, page }, { onUnauthorized } = {}) {
  const key = [categoryId, search, page].join("|");
  const [state, setState] = useState({ key, status: "loading", items: [], pagination: null });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    setState({ key, status: "loading", items: [], pagination: null });
    listStock(token, {
      categoryId: categoryId || undefined,
      search: search || undefined,
      page,
      pageSize: STOCK_PAGE_SIZE,
      signal: controller.signal,
    })
      .then((res) => {
        if (!cancelled) setState({ key, status: "ready", items: res.data, pagination: res.pagination });
      })
      .catch((err) => {
        if (cancelled || err?.name === "AbortError") return;
        if (err?.status === 401) {
          onUnauthorized?.();
          return;
        }
        setState({ key, status: "error", items: [], pagination: null });
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, key, reloadKey]);

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}
