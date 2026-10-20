export const DASHBOARD_RANGES = [
  { id: "today", label: "Hari ini", days: 1 },
  { id: "7d", label: "7 hari", days: 7 },
  { id: "30d", label: "30 hari", days: 30 },
];

const DAY_MS = 24 * 60 * 60 * 1000;
const WIB_OFFSET_MS = 7 * 60 * 60 * 1000; // WIB = UTC+7, sama dengan backend

// Tanggal "YYYY-MM-DD" menurut WIB, apa pun zona waktu perangkatnya.
const ymd = (ms) => new Date(ms).toISOString().slice(0, 10);

export function rangeDates(rangeId, now = new Date()) {
  const range = DASHBOARD_RANGES.find((r) => r.id === rangeId) ?? DASHBOARD_RANGES[0];
  const wibNow = now.getTime() + WIB_OFFSET_MS;
  return { startDate: ymd(wibNow - (range.days - 1) * DAY_MS), endDate: ymd(wibNow) };
}

// "2026-10-20" -> "20/10/2026"
export function formatDay(text) {
  const [y, m, d] = String(text).split("-");
  return `${d}/${m}/${y}`;
}

export function rangeLabel(startDate, endDate) {
  return startDate === endDate ? formatDay(startDate) : `${formatDay(startDate)} – ${formatDay(endDate)}`;
}

export const formatHour = (hour) => `${String(hour).padStart(2, "0")}.00`;

// Tinggi batang 0-100 relatif terhadap jam tersibuk. Jam ada order minimal 4% supaya tetap kelihatan.
export function peakBars(hours) {
  const max = Math.max(0, ...hours.map((h) => h.orders));
  return hours.map((h) => ({
    hour: h.hour,
    orders: h.orders,
    pct: max === 0 || h.orders === 0 ? 0 : Math.max(4, Math.round((h.orders / max) * 100)),
  }));
}

// Jam tersibuk "12.00–13.00"; kalau sama banyak, yang paling pagi. Null kalau belum ada order.
export function busiestHour(hours) {
  let best = null;
  for (const h of hours) {
    if (h.orders > 0 && (best === null || h.orders > best.orders)) best = h;
  }
  return best ? `${formatHour(best.hour)}–${formatHour((best.hour + 1) % 24)}` : null;
}

export const hasSales = (summary) => Boolean(summary) && summary.orders > 0;
