import { describe, it, expect, vi, afterEach } from "vitest";
import { verifyPickupManual } from "../src/services/staffApi";
import { canManualPickup, filterPickupOrders } from "../src/features/pickup/pickup";

afterEach(() => vi.unstubAllGlobals());

describe("pickup manual", () => {
  it("hanya kasir dan admin yang boleh", () => {
    expect(canManualPickup("CASHIER")).toBe(true);
    expect(canManualPickup("ADMIN")).toBe(true);
    expect(canManualPickup("PICKUP")).toBe(false);
    expect(canManualPickup("KITCHEN")).toBe(false);
  });

  const rows = [
    { order_number: "A033", customer_name: "Uki" },
    { order_number: "A034", customer_name: "Budi" },
  ];
  it("cari lewat nomor atau nama, tanpa peduli huruf besar/kecil", () => {
    expect(filterPickupOrders(rows, "a033")).toHaveLength(1);
    expect(filterPickupOrders(rows, "BUDI")[0].order_number).toBe("A034");
    expect(filterPickupOrders(rows, "  ")).toHaveLength(2);
    expect(filterPickupOrders(rows, "zzz")).toHaveLength(0);
  });

  it("verifyPickupManual memanggil POST /pickup/{id}/verify-manual dengan token staf", async () => {
    const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: {} }) });
    vi.stubGlobal("fetch", fn);
    await verifyPickupManual("tokstaf", "pid-1");
    const [url, opts] = fn.mock.calls[0];
    expect(url).toMatch(/\/pickup\/pid-1\/verify-manual$/);
    expect(opts.method).toBe("POST");
    expect(JSON.stringify(opts.headers)).toContain("tokstaf");
  });
});
