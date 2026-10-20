import { describe, it, expect, vi, afterEach } from "vitest";
import { adjustStock, listStock } from "../src/services/staffApi";
import {
  buildAdjustBody,
  describeStockError,
  isAdjustValid,
  parseQty,
  signedDelta,
  stockAfter,
  stockLabel,
} from "../src/features/admin/stock";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("API stok", () => {
  it("listStock mengirim filter dan halaman ke /inventory", async () => {
    const fn = mockFetch();
    await listStock("tkn", { categoryId: "c1", search: "teh", page: 2, pageSize: 20 });
    const url = fn.mock.calls[0][0];
    expect(url).toContain("/inventory?");
    expect(url).toContain("category_id=c1");
    expect(url).toContain("search=teh");
    expect(url).toContain("page=2");
  });

  it("listStock tanpa filter tidak mengirim parameter kosong", async () => {
    const fn = mockFetch();
    await listStock("tkn");
    const url = fn.mock.calls[0][0];
    expect(url).not.toContain("category_id");
    expect(url).not.toContain("search");
  });

  it("adjustStock memakai POST ke /inventory/{id}/adjust", async () => {
    const fn = mockFetch();
    await adjustStock("tkn", "p1", { quantity: 5, reason: "belanja", movement_type: "RESTOCK" });
    expect(fn.mock.calls[0][0]).toContain("/inventory/p1/adjust");
    expect(fn.mock.calls[0][1].method).toBe("POST");
    expect(JSON.parse(fn.mock.calls[0][1].body).quantity).toBe(5);
  });
});

describe("jumlah dan pratinjau", () => {
  it("parseQty hanya menerima angka bulat 1..100000", () => {
    expect(parseQty("10")).toBe(10);
    expect(parseQty(" 7 ")).toBe(7);
    expect(parseQty("100000")).toBe(100000);
    expect(parseQty("100001")).toBeNull();
    expect(parseQty("0")).toBeNull();
    expect(parseQty("-3")).toBeNull();
    expect(parseQty("2.5")).toBeNull();
    expect(parseQty("")).toBeNull();
  });

  it("tanda perubahan mengikuti jenis koreksi", () => {
    expect(signedDelta("add", "10")).toBe(10);
    expect(signedDelta("reduce", "4")).toBe(-4);
    expect(signedDelta("waste", "2")).toBe(-2);
    expect(signedDelta("add", "x")).toBeNull();
  });

  it("stockAfter menghitung stok sesudah koreksi", () => {
    expect(stockAfter(25, "add", "15")).toBe(40);
    expect(stockAfter(25, "waste", "5")).toBe(20);
    expect(stockAfter(25, "add", "")).toBeNull();
  });
});

describe("validasi dan isi permintaan", () => {
  it("valid kalau jumlah benar, alasan cukup, dan stok tidak minus", () => {
    expect(isAdjustValid(10, "add", "5", "belanja pasar")).toBe(true);
    expect(isAdjustValid(10, "waste", "10", "basi")).toBe(true); // jadi 0, masih boleh
    expect(isAdjustValid(10, "waste", "11", "basi")).toBe(false); // minus
    expect(isAdjustValid(10, "add", "5", "  ab ")).toBe(false); // alasan < 3 huruf
    expect(isAdjustValid(10, "add", "", "belanja")).toBe(false);
  });

  it("buildAdjustBody mengirim jumlah bertanda, alasan rapi, dan jenisnya", () => {
    expect(buildAdjustBody("waste", "3", "  tumpah ")).toEqual({
      quantity: -3,
      reason: "tumpah",
      movement_type: "WASTE",
    });
    expect(buildAdjustBody("add", "20", "restock").movement_type).toBe("RESTOCK");
    expect(buildAdjustBody("reduce", "1", "hitung ulang").movement_type).toBe("ADJUSTMENT");
  });

  it("stockLabel menandai stok habis", () => {
    expect(stockLabel({ quantity_available: 0 })).toBe("Habis");
    expect(stockLabel({ quantity_available: 3 })).toBeNull();
  });
});

describe("pesan error stok", () => {
  it("memetakan kode backend ke bahasa staf", () => {
    expect(describeStockError({ code: "ADJUST_EXCEEDS_STOCK" })).toContain("Stok tidak cukup");
    expect(describeStockError({ code: "PRODUCT_NOT_FOUND" })).toContain("tidak ditemukan");
    expect(describeStockError({ status: 403 })).toContain("admin");
    expect(describeStockError({ status: 422 })).toContain("Periksa isian");
    expect(describeStockError(new Error("offline"))).toContain("Periksa angka stok");
  });
});
