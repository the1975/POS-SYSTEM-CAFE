import { describe, it, expect, vi, afterEach } from "vitest";
import { getProducts } from "../src/services/menuApi";

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}
// URL bisa relatif (/api/v1/...), jadi diberi base agar bisa di-parse.
const calledParams = (fn) => new URL(fn.mock.calls[0][0], "http://localhost").searchParams;

afterEach(() => vi.unstubAllGlobals());

describe("getProducts", () => {
  it("mengirim hanya parameter yang diisi", async () => {
    const fn = mockFetch();
    await getProducts({});
    const p = calledParams(fn);
    expect(p.get("page")).toBe("1");
    expect(p.get("page_size")).toBe("20");
    expect(p.has("category_id")).toBe(false);
    expect(p.has("search")).toBe(false);
  });

  it("menyertakan kategori, pencarian, dan halaman", async () => {
    const fn = mockFetch();
    await getProducts({ categoryId: "abc", search: "nasi goreng", page: 2 });
    const p = calledParams(fn);
    expect(p.get("category_id")).toBe("abc");
    expect(p.get("search")).toBe("nasi goreng"); // spasi ter-encode lalu terbaca utuh
    expect(p.get("page")).toBe("2");
  });
});
