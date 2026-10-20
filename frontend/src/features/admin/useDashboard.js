import { useEffect, useState } from "react";
import { getPeakHours, getSalesSummary, getTopProducts } from "../../services/staffApi";
import { rangeDates } from "./dashboard";

// status: loading | ready | error. Tiga laporan diambil bersamaan; ganti rentang = ambil ulang.
export function useDashboard(token, rangeId, { onUnauthorized } = {}) {
  const [state, setState] = useState({ status: "loading", range: null, summary: null, top: [], hours: [] });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const range = rangeDates(rangeId);
    const opts = { ...range, signal: controller.signal };
    setState({ status: "loading", range, summary: null, top: [], hours: [] });
    Promise.all([getSalesSummary(token, opts), getTopProducts(token, opts), getPeakHours(token, opts)])
      .then(([summary, top, hours]) => {
        if (!cancelled) {
          setState({ status: "ready", range, summary: summary.data, top: top.data, hours: hours.data });
        }
      })
      .catch((err) => {
        if (cancelled || err?.name === "AbortError") return;
        if (err?.status === 401) {
          onUnauthorized?.();
          return;
        }
        setState({ status: "error", range, summary: null, top: [], hours: [] });
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, rangeId, reloadKey]);

  return { ...state, reload: () => setReloadKey((k) => k + 1) };
}
