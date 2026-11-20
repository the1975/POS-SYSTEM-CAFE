import { describe, it, expect, vi, afterEach } from "vitest";
import { setReorderLevel } from "../src/services/staffApi";
import { parseReorderLevel, stockLabel } from "../src/features/admin/stock";

afterEach(() => vi.unstubAllGlobals());

describe("batas minimum stok", () => {
  it("stockLabel: Habis, Menipis, atau tidak ada tanda", () => {
    expect(stockLabel({ quantity_available: 0, reorder_level: 5 })).toBe("Habis");
    expect(stockLabel({ quantity_available: 5, reorder_level: 5 })).toBe("Menipis");
    expect(stockLabel({ quantity_available: 3, reorder_level: 5 })).toBe("Menipis");
    expect(stockLabel({ quantity_available: 6, reorder_level: 5 })).toBeNull();
    expect(stockLabel({ quantity_available: 2, reorder_level: 0 })).toBeNull();
    expect(stockLabel({ quantity_available: 2 })).toBeNull();
  });

  it("parseReorderLevel menerima 0..100000 saja", () => {
    expect(parseReorderLevel("0")).toBe(0);
    expect(parseReorderLevel(" 12 ")).toBe(12);
    expect(parseReorderLevel("100000")).toBe(100000);
    expect(parseReorderLevel("100001")).toBeNull();
    expect(parseReorderLevel("-1")).toBeNull();
    expect(parseReorderLevel("1.5")).toBeNull();
    expect(parseReorderLevel("")).toBeNull();
  });

  it("setReorderLevel memanggil PATCH /inventory/{id}/reorder-level", async () => {
    const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: {} }) });
    vi.stubGlobal("fetch", fn);
    await setReorderLevel("tokadmin", "pid-1", 4);
    const [url, opts] = fn.mock.calls[0];
    expect(url).toMatch(/\/inventory\/pid-1\/reorder-level$/);
    expect(opts.method).toBe("PATCH");
    expect(JSON.parse(opts.body)).toEqual({ reorder_level: 4 });
    expect(JSON.stringify(opts.headers)).toContain("tokadmin");
  });
});
