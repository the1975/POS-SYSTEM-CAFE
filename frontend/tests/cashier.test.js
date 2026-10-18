import { describe, it, expect, vi, afterEach } from "vitest";
import { ApiError } from "../src/services/api";
import { confirmCash, listStaffOrders } from "../src/services/staffApi";
import { changeFor, parseRupiahInput, quickAmounts } from "../src/features/cashier/cash";
import { describeCashError } from "../src/features/cashier/errors";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("staffApi", () => {
  it("listStaffOrders memfilter WAITING_CASH, mencari, dan mengirim token lewat header", async () => {
    const fn = mockFetch();
    await listStaffOrders("tkn-1", { paymentStatus: "WAITING_CASH", search: "A127" });
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/staff/orders?");
    expect(url).toContain("payment_status=WAITING_CASH");
    expect(url).toContain("search=A127");
    expect(url).not.toContain("tkn-1");
    expect(options.headers.Authorization).toBe("Bearer tkn-1");
  });

  it("listStaffOrders tanpa pencarian tidak mengirim parameter search", async () => {
    const fn = mockFetch();
    await listStaffOrders("tkn-1", { paymentStatus: "WAITING_CASH" });
    expect(fn.mock.calls[0][0]).not.toContain("search=");
  });

  it("confirmCash hanya mengirim cash_received (kembalian dihitung backend)", async () => {
    const fn = mockFetch();
    await confirmCash("tkn-1", "pay-9", 100000);
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/payments/pay-9/cash-confirm");
    expect(options.method).toBe("POST");
    expect(options.headers.Authorization).toBe("Bearer tkn-1");
    expect(JSON.parse(options.body)).toEqual({ cash_received: "100000" });
  });
});

describe("hitung uang", () => {
  it("parseRupiahInput mengambil angka saja dan membatasi panjang", () => {
    expect(parseRupiahInput("Rp100.000")).toBe(100000);
    expect(parseRupiahInput("abc")).toBe(0);
    expect(parseRupiahInput("")).toBe(0);
    expect(parseRupiahInput(null)).toBe(0);
    expect(parseRupiahInput("12345678901234")).toBe(123456789);
  });

  it("changeFor menghitung kembalian dan tidak pernah negatif", () => {
    expect(changeFor(62700, 100000)).toBe(37300);
    expect(changeFor(62700, 62700)).toBe(0);
    expect(changeFor(62700, 50000)).toBe(0);
  });

  it("quickAmounts: uang pas lalu pecahan yang cukup", () => {
    expect(quickAmounts(62700)).toEqual([62700, 100000]);
    expect(quickAmounts(15000)).toEqual([15000, 20000, 50000, 100000]);
    expect(quickAmounts(120000)).toEqual([120000]);
    expect(quickAmounts(62700.5)).toEqual([62701, 100000]);
  });
});

describe("pesan error kasir", () => {
  it("memetakan kode backend ke pesan yang jelas", () => {
    expect(describeCashError(new ApiError(422, "INSUFFICIENT_CASH", "x"))).toMatch(/belum mencukupi/);
    expect(describeCashError(new ApiError(409, "PAYMENT_ALREADY_PAID", "x"))).toMatch(/sudah dikonfirmasi/);
    expect(describeCashError(new ApiError(409, "PAYMENT_INVALID_STATE", "x"))).toMatch(/tidak bisa dibayar/);
    expect(describeCashError(new ApiError(403, "FORBIDDEN", "x"))).toMatch(/tidak boleh/);
  });

  it("saat gagal jaringan/server, menyuruh periksa antrean (hasil tidak pasti)", () => {
    expect(describeCashError(new ApiError(500, "INTERNAL_ERROR", "x"))).toMatch(/Periksa antrean/);
    expect(describeCashError(new TypeError("Failed to fetch"))).toMatch(/Periksa antrean/);
  });
});
