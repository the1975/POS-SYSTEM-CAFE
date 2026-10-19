import { useEffect, useState } from "react";
import { listRoles, listUsers } from "../../services/staffApi";

export const USERS_PAGE_SIZE = 20;

// status: loading | ready | error. Tanpa polling: daftar akun jarang berubah.
export function useUsers(token, { roleId, isActive, search, page }, { onUnauthorized } = {}) {
  const key = [roleId, isActive, search, page].join("|");
  const [state, setState] = useState({ key, status: "loading", users: [], pagination: null });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    setState({ key, status: "loading", users: [], pagination: null });
    listUsers(token, {
      roleId: roleId || undefined,
      isActive,
      search: search || undefined,
      page,
      pageSize: USERS_PAGE_SIZE,
      signal: controller.signal,
    })
      .then((res) => {
        if (!cancelled) setState({ key, status: "ready", users: res.data, pagination: res.pagination });
      })
      .catch((err) => {
        if (cancelled || err?.name === "AbortError") return;
        if (err?.status === 401) {
          onUnauthorized?.();
          return;
        }
        setState({ key, status: "error", users: [], pagination: null });
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, key, reloadKey]);

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}

export function useRoles(token, onUnauthorized) {
  const [state, setState] = useState({ status: "loading", roles: [] });
  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    listRoles(token, { signal: controller.signal })
      .then((res) => {
        if (!cancelled) setState({ status: "ready", roles: res.data });
      })
      .catch((err) => {
        if (cancelled || err?.name === "AbortError") return;
        if (err?.status === 401) {
          onUnauthorized?.();
          return;
        }
        setState({ status: "error", roles: [] });
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);
  return state;
}
