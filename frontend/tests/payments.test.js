import { describe, it, expect, vi, afterEach } from "vitest";
import { createQris } from "../src/services/paymentApi";

afterEach(() => vi.unstubAllGlobals());

describe("createQris", () => {
  it("POST /payments/qris dengan order_id di body dan token di header", async () => {
    const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: {} }) });
    vi.stubGlobal("fetch", fn);
    await createQris("abc", "tok123");
    const [url, opts] = fn.mock.calls[0];
    expect(url).toMatch(/\/payments\/qris$/);
    expect(opts.method).toBe("POST");
    expect(opts.headers["X-Tracking-Token"]).toBe("tok123");
    expect(JSON.parse(opts.body)).toEqual({ order_id: "abc" });
  });
});
