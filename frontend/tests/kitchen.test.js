import { describe, it, expect, vi, afterEach } from "vitest";
import { ApiError } from "../src/services/api";
import { listKitchenOrders, markItemReady, remakeItem, startOrder } from "../src/services/staffApi";
import {
  REMAKE_REASONS,
  canMarkReady,
  canRemake,
  elapsedMinutes,
  formatElapsed,
  itemStatusLabel,
  mergeOrder,
  splitQueue,
} from "../src/features/kitchen/kitchen";
import { describeKitchenError } from "../src/features/kitchen/errors";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("kitchenApi", () => {
  it("listKitchenOrders memakai token lewat header", async () => {
    const fn = mockFetch();
    await listKitchenOrders("tkn-1");
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/kitchen/orders");
    expect(url).not.toContain("tkn-1");
    expect(options.headers.Authorization).toBe("Bearer tkn-1");
  });

  it("startOrder dan markItemReady memakai POST ke alamat yang benar", async () => {
    const fn = mockFetch();
    await startOrder("tkn-1", "o-1");
    await markItemReady("tkn-1", "i-1");
    expect(fn.mock.calls[0][0]).toContain("/kitchen/orders/o-1/start");
    expect(fn.mock.calls[0][1].method).toBe("POST");
    expect(fn.mock.calls[1][0]).toContain("/kitchen/order-items/i-1/ready");
    expect(fn.mock.calls[1][1].method).toBe("POST");
  });

  it("remakeItem mengirim alasan dan catatan; catatan kosong tidak dikirim", async () => {
    const fn = mockFetch();
    await remakeItem("tkn-1", "i-1", { reason: "WRONG_MENU", notes: "  salah es  " });
    await remakeItem("tkn-1", "i-1", { reason: "OTHER", notes: "   " });
    expect(fn.mock.calls[0][0]).toContain("/kitchen/order-items/i-1/remake");
    expect(JSON.parse(fn.mock.calls[0][1].body)).toEqual({ reason: "WRONG_MENU", notes: "salah es" });
    expect(JSON.parse(fn.mock.calls[1][1].body)).toEqual({ reason: "OTHER" });
  });
});

describe("antrean dapur", () => {
  const A = { order_id: "a", status: "PREPARING" };
  const B = { order_id: "b", status: "CONFIRMED" };

  it("splitQueue memisahkan sedang dimasak dan antre", () => {
    expect(splitQueue([A, B])).toEqual({ cooking: [A], waiting: [B] });
  });

  it("mergeOrder mengganti, menambah, dan membuang order yang tidak aktif", () => {
    const updated = { order_id: "b", status: "PREPARING" };
    expect(mergeOrder([A, B], updated)).toEqual([A, updated]);
    expect(mergeOrder([A], B)).toEqual([A, B]);
    expect(mergeOrder([A, B], { order_id: "a", status: "READY" })).toEqual([B]);
  });
});

describe("item dan waktu", () => {
  it("aturan tombol sesuai backend", () => {
    expect(canMarkReady({ status: "PREPARING" })).toBe(true);
    expect(canMarkReady({ status: "REMAKE" })).toBe(true);
    expect(canMarkReady({ status: "READY" })).toBe(false);
    expect(canRemake({ status: "PREPARING" })).toBe(true);
    expect(canRemake({ status: "READY" })).toBe(true);
    expect(canRemake({ status: "REMAKE" })).toBe(false);
    expect(canRemake({ status: "PENDING" })).toBe(false);
  });

  it("elapsedMinutes dan formatElapsed", () => {
    const now = Date.parse("2026-10-18T10:00:00Z");
    expect(elapsedMinutes("2026-10-18T09:48:00Z", now)).toBe(12);
    expect(elapsedMinutes("2026-10-18T10:05:00Z", now)).toBe(0);
    expect(elapsedMinutes(null, now)).toBeNull();
    expect(formatElapsed(null)).toBe("—");
    expect(formatElapsed(0)).toBe("baru saja");
    expect(formatElapsed(12)).toBe("12 mnt");
    expect(formatElapsed(65)).toBe("1 j 5 mnt");
  });

  it("label status item dan daftar alasan remake", () => {
    expect(itemStatusLabel("REMAKE")).toBe("Dibuat ulang");
    expect(itemStatusLabel("APA_INI")).toBe("APA_INI");
    expect(REMAKE_REASONS.map((r) => r.value)).toContain("WRONG_MENU");
    expect(new Set(REMAKE_REASONS.map((r) => r.value)).size).toBe(REMAKE_REASONS.length);
  });
});

describe("pesan error dapur", () => {
  it("memetakan kode backend ke pesan yang jelas", () => {
    expect(describeKitchenError(new ApiError(409, "KITCHEN_INVALID_STATE", "x"))).toMatch(/sudah berubah/);
    expect(describeKitchenError(new ApiError(409, "REMAKE_ALREADY_IN_PROGRESS", "x"))).toMatch(/sudah dalam proses/);
    expect(describeKitchenError(new ApiError(409, "ORDER_NOT_PAID", "x"))).toMatch(/belum dibayar/);
    expect(describeKitchenError(new ApiError(403, "FORBIDDEN", "x"))).toMatch(/tidak boleh/);
    expect(describeKitchenError(new TypeError("Failed to fetch"))).toMatch(/Periksa antrean/);
  });
});
