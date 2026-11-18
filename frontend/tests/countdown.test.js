import { describe, it, expect, vi, afterEach } from "vitest";
import { cancelOrder } from "../src/services/orderApi";
import { canCancel, formatCountdown, secondsLeft } from "../src/features/orders/countdown";

afterEach(() => vi.unstubAllGlobals());

describe("hitung mundur", () => {
  const now = Date.parse("2026-11-18T10:00:00Z");
  it("sisa detik dibulatkan ke atas dan tidak negatif", () => {
    expect(secondsLeft("2026-11-18T10:07:00Z", now)).toBe(420);
    expect(secondsLeft("2026-11-18T10:00:00.400Z", now)).toBe(1);
    expect(secondsLeft("2026-11-18T09:59:00Z", now)).toBe(0);
  });
  it("null bila tidak ada atau tidak valid", () => {
    expect(secondsLeft(null, now)).toBeNull();
    expect(secondsLeft("bukan-tanggal", now)).toBeNull();
  });
  it("format menit:detik", () => {
    expect(formatCountdown(402)).toBe("6:42");
    expect(formatCountdown(65)).toBe("1:05");
    expect(formatCountdown(0)).toBe("0:00");
    expect(formatCountdown(-5)).toBe("0:00");
  });
  it("hanya PENDING yang bisa dibatalkan", () => {
    expect(canCancel({ status: "PENDING" })).toBe(true);
    expect(canCancel({ status: "CONFIRMED" })).toBe(false);
    expect(canCancel(null)).toBe(false);
  });
});

describe("cancelOrder", () => {
  it("POST ke /orders/{id}/cancel dengan token di header", async () => {
    const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: {} }) });
    vi.stubGlobal("fetch", fn);
    await cancelOrder("abc", "tok123");
    const [url, opts] = fn.mock.calls[0];
    expect(url).toMatch(/\/orders\/abc\/cancel$/);
    expect(opts.method).toBe("POST");
    expect(opts.headers["X-Tracking-Token"]).toBe("tok123");
  });
});
