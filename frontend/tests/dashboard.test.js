import { describe, it, expect, vi, afterEach } from "vitest";
import { getPeakHours, getSalesSummary, getTopProducts } from "../src/services/staffApi";
import {
  busiestHour,
  formatDay,
  formatHour,
  hasSales,
  peakBars,
  rangeDates,
  rangeLabel,
} from "../src/features/admin/dashboard";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("API laporan", () => {
  const range = { startDate: "2026-10-20", endDate: "2026-10-21" };

  it("getSalesSummary mengirim rentang tanggal ke /analytics/summary", async () => {
    const fn = mockFetch();
    await getSalesSummary("tkn", range);
    const url = fn.mock.calls[0][0];
    expect(url).toContain("/analytics/summary?");
    expect(url).toContain("start_date=2026-10-20");
    expect(url).toContain("end_date=2026-10-21");
  });

  it("getTopProducts mengirim limit, default 5", async () => {
    const fn = mockFetch();
    await getTopProducts("tkn", range);
    expect(fn.mock.calls[0][0]).toContain("/analytics/products/top?");
    expect(fn.mock.calls[0][0]).toContain("limit=5");
  });

  it("getPeakHours memakai /analytics/peak-hours", async () => {
    const fn = mockFetch();
    await getPeakHours("tkn", range);
    expect(fn.mock.calls[0][0]).toContain("/analytics/peak-hours?");
  });
});

describe("rentang tanggal WIB", () => {
  it("memakai tanggal WIB, bukan tanggal UTC", () => {
    // 20 Okt 20.00 UTC = 21 Okt 03.00 WIB
    const now = new Date("2026-10-20T20:00:00Z");
    expect(rangeDates("today", now)).toEqual({ startDate: "2026-10-21", endDate: "2026-10-21" });
    expect(rangeDates("7d", now)).toEqual({ startDate: "2026-10-15", endDate: "2026-10-21" });
    expect(rangeDates("30d", now)).toEqual({ startDate: "2026-09-22", endDate: "2026-10-21" });
  });

  it("siang hari UTC masih tanggal yang sama di WIB", () => {
    const now = new Date("2026-10-20T10:00:00Z");
    expect(rangeDates("today", now).endDate).toBe("2026-10-20");
  });

  it("rentang tidak dikenal jatuh ke Hari ini", () => {
    const now = new Date("2026-10-20T10:00:00Z");
    expect(rangeDates("xyz", now)).toEqual({ startDate: "2026-10-20", endDate: "2026-10-20" });
  });

  it("label tanggal mudah dibaca", () => {
    expect(formatDay("2026-10-20")).toBe("20/10/2026");
    expect(rangeLabel("2026-10-20", "2026-10-20")).toBe("20/10/2026");
    expect(rangeLabel("2026-10-14", "2026-10-20")).toBe("14/10/2026 – 20/10/2026");
  });
});

describe("grafik jam ramai", () => {
  const hours = Array.from({ length: 24 }, (_, h) => ({ hour: h, orders: 0 }));
  const sample = hours.map((h) => (h.hour === 10 ? { ...h, orders: 2 } : h.hour === 12 ? { ...h, orders: 8 } : h));

  it("tinggi batang relatif ke jam tersibuk", () => {
    const bars = peakBars(sample);
    expect(bars).toHaveLength(24);
    expect(bars[12].pct).toBe(100);
    expect(bars[10].pct).toBe(25);
    expect(bars[0].pct).toBe(0);
  });

  it("jam yang ada order minimal tetap kelihatan", () => {
    const tiny = hours.map((h) => (h.hour === 3 ? { ...h, orders: 1 } : h.hour === 4 ? { ...h, orders: 500 } : h));
    expect(peakBars(tiny)[3].pct).toBe(4);
  });

  it("tanpa order semua batang 0", () => {
    expect(peakBars(hours).every((b) => b.pct === 0)).toBe(true);
  });

  it("jam tersibuk diformat, yang paling pagi menang kalau seri, null kalau kosong", () => {
    expect(busiestHour(sample)).toBe("12.00–13.00");
    const tie = hours.map((h) => (h.hour === 9 || h.hour === 14 ? { ...h, orders: 3 } : h));
    expect(busiestHour(tie)).toBe("09.00–10.00");
    expect(busiestHour(hours)).toBeNull();
    expect(busiestHour(hours.map((h) => (h.hour === 23 ? { ...h, orders: 1 } : h)))).toBe("23.00–00.00");
  });

  it("formatHour dan hasSales", () => {
    expect(formatHour(7)).toBe("07.00");
    expect(hasSales({ orders: 3 })).toBe(true);
    expect(hasSales({ orders: 0 })).toBe(false);
    expect(hasSales(null)).toBe(false);
  });
});
