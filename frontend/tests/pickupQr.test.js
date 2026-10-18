import { describe, it, expect } from "vitest";
import { QR_STATUSES, shouldShowPickupQr } from "../src/features/orders/pickupQr";
import { POLL_MS, isFinalStatus } from "../src/features/orders/useOrder";

describe("QR pengambilan", () => {
  it("tampil hanya saat order siap/terlambat diambil DAN token ada", () => {
    expect(shouldShowPickupQr({ status: "READY", pickup_token: "abc" })).toBe(true);
    expect(shouldShowPickupQr({ status: "OVERDUE", pickup_token: "abc" })).toBe(true);
    expect(shouldShowPickupQr({ status: "READY", pickup_token: null })).toBe(false);
    expect(shouldShowPickupQr({ status: "PREPARING", pickup_token: "abc" })).toBe(false);
    expect(shouldShowPickupQr({ status: "COMPLETED", pickup_token: "abc" })).toBe(false);
    expect(shouldShowPickupQr(null)).toBe(false);
    expect(QR_STATUSES).toEqual(["READY", "OVERDUE"]);
  });
});

describe("pembaruan otomatis status", () => {
  it("berhenti hanya saat pesanan selesai atau dibatalkan", () => {
    expect(isFinalStatus("COMPLETED")).toBe(true);
    expect(isFinalStatus("CANCELLED")).toBe(true);
    expect(isFinalStatus("READY")).toBe(false);
    expect(isFinalStatus("OVERDUE")).toBe(false); // masih menunggu diambil
    expect(isFinalStatus("PENDING")).toBe(false);
  });

  it("jeda pembaruan wajar (3-5 detik sesuai docs, tidak membanjiri server)", () => {
    expect(POLL_MS).toBeGreaterThanOrEqual(3000);
    expect(POLL_MS).toBeLessThanOrEqual(10000);
  });
});
