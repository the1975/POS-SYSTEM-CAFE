import { useEffect, useState } from "react";
import { getCategories } from "../../services/menuApi";
import { listAdminProducts } from "../../services/staffApi";
import { PRODUCTS_PAGE_SIZE } from "./products";

// status: loading | ready | error. Tanpa polling: daftar produk jarang berubah.
export function useAdminProducts(token, { categoryId, isAvailable, search, page }, { onUnauthorized } = {}) {
  const key = [categoryId, isAvailable, search, page].join("|");
  const [state, setState] = useState({ key, status: "loading", products: [], pagination: null });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    setState({ key, status: "loading", products: [], pagination: null });
    listAdminProducts(token, {
      categoryId: categoryId || undefined,
      isAvailable,
      search: search || undefined,
      page,
      pageSize: PRODUCTS_PAGE_SIZE,
      signal: controller.signal,
    })
      .then((res) => {
        if (!cancelled) setState({ key, status: "ready", products: res.data, pagination: res.pagination });
      })
      .catch((err) => {
        if (cancelled || err?.name === "AbortError") return;
        if (err?.status === 401) {
          onUnauthorized?.();
          return;
        }
        setState({ key, status: "error", products: [], pagination: null });
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, key, reloadKey]);

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}

// Kategori untuk pilihan di form/filter (kategori nonaktif tidak ikut: memang tidak tampil di menu).
export function useCategories() {
  const [state, setState] = useState({ status: "loading", categories: [] });
  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    getCategories({ signal: controller.signal })
      .then((res) => {
        if (!cancelled) setState({ status: "ready", categories: res.data });
      })
      .catch((err) => {
        if (cancelled || err?.name === "AbortError") return;
        setState({ status: "error", categories: [] });
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, []);
  return state;
}
