import { describe, it, expect, vi, afterEach } from "vitest";
import { createProduct, listAdminProducts, updateProduct } from "../src/services/staffApi";
import {
  buildProductBody,
  buildProductPatch,
  describeProductError,
  emptyProductForm,
  formFromProduct,
  isProductFormValid,
  isSellingAtLoss,
  moneyHint,
  parseRupiah,
} from "../src/features/admin/products";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

const product = {
  id: "p1",
  category_id: "c1",
  category_name: "Minuman",
  name: "Es Teh",
  description: "Segar",
  price: 8000,
  cost_price: 3000,
  image_url: null,
  is_available: true,
};

describe("API produk admin", () => {
  it("listAdminProducts mengirim filter dan halaman ke /admin/products", async () => {
    const fn = mockFetch();
    await listAdminProducts("tkn", { categoryId: "c1", isAvailable: "false", search: "teh", page: 2, pageSize: 20 });
    const url = fn.mock.calls[0][0];
    expect(url).toContain("/admin/products?");
    expect(url).toContain("category_id=c1");
    expect(url).toContain("is_available=false");
    expect(url).toContain("search=teh");
    expect(url).toContain("page=2");
  });

  it("listAdminProducts tanpa filter tidak mengirim parameter kosong", async () => {
    const fn = mockFetch();
    await listAdminProducts("tkn");
    const url = fn.mock.calls[0][0];
    expect(url).not.toContain("category_id");
    expect(url).not.toContain("is_available");
    expect(url).not.toContain("search");
  });

  it("createProduct dan updateProduct memakai metode yang benar", async () => {
    const fn = mockFetch();
    await createProduct("tkn", { name: "X" });
    await updateProduct("tkn", "p1", { price: 9000 });
    expect(fn.mock.calls[0][0]).toMatch(/\/products$/);
    expect(fn.mock.calls[0][1].method).toBe("POST");
    expect(fn.mock.calls[1][0]).toContain("/products/p1");
    expect(fn.mock.calls[1][1].method).toBe("PATCH");
    expect(JSON.parse(fn.mock.calls[1][1].body)).toEqual({ price: 9000 });
  });
});

describe("isian uang", () => {
  it("parseRupiah hanya menerima angka bulat", () => {
    expect(parseRupiah("25000")).toBe(25000);
    expect(parseRupiah("  8000 ")).toBe(8000);
    expect(parseRupiah("")).toBeNull();
    expect(parseRupiah("12.5")).toBeNull();
    expect(parseRupiah("-5")).toBeNull();
    expect(parseRupiah("abc")).toBeNull();
  });

  it("moneyHint menampilkan Rupiah atau kosong", () => {
    expect(moneyHint("25000")).toBe("= Rp25.000");
    expect(moneyHint("x")).toBe("");
  });
});

describe("form produk", () => {
  const filled = { ...emptyProductForm("c1"), name: " Teh Tarik ", price: "12000", costPrice: "5000" };

  it("valid kalau nama, kategori, harga, dan HPP benar", () => {
    expect(isProductFormValid(filled)).toBe(true);
    expect(isProductFormValid({ ...filled, name: "   " })).toBe(false);
    expect(isProductFormValid({ ...filled, categoryId: "" })).toBe(false);
    expect(isProductFormValid({ ...filled, price: "" })).toBe(false);
    expect(isProductFormValid({ ...filled, costPrice: "1,5" })).toBe(false);
  });

  it("peringatan rugi saat HPP lebih besar dari harga jual", () => {
    expect(isSellingAtLoss(filled)).toBe(false);
    expect(isSellingAtLoss({ ...filled, price: "4000" })).toBe(true);
    expect(isSellingAtLoss({ ...filled, price: "" })).toBe(false);
  });

  it("buildProductBody merapikan teks dan mengubah kosong jadi null", () => {
    expect(buildProductBody(filled)).toEqual({
      category_id: "c1",
      name: "Teh Tarik",
      description: null,
      price: 12000,
      cost_price: 5000,
      image_url: null,
      is_available: true,
    });
  });

  it("buildProductPatch hanya berisi field yang berubah", () => {
    const form = formFromProduct(product);
    expect(buildProductPatch(product, form)).toEqual({});
    expect(buildProductPatch(product, { ...form, price: "9000" })).toEqual({ price: 9000 });
    expect(buildProductPatch(product, { ...form, isAvailable: false })).toEqual({ is_available: false });
    expect(buildProductPatch(product, { ...form, description: "  " })).toEqual({ description: null });
    expect(buildProductPatch(product, { ...form, name: " Es Teh Manis " })).toEqual({ name: "Es Teh Manis" });
  });

  it("harga berdesimal dari database tidak dianggap berubah kalau isian tidak diubah", () => {
    const p = { ...product, price: 8000.4 };
    expect(buildProductPatch(p, formFromProduct(p))).toEqual({});
  });
});

describe("pesan error produk", () => {
  it("memetakan kode backend ke bahasa staf", () => {
    expect(describeProductError({ code: "INVALID_CATEGORY" })).toContain("Kategori");
    expect(describeProductError({ code: "PRODUCT_NOT_FOUND" })).toContain("tidak ditemukan");
    expect(describeProductError({ status: 403 })).toContain("admin");
    expect(describeProductError({ status: 422 })).toContain("Periksa isian");
    expect(describeProductError(new Error("offline"))).toContain("Periksa daftar produk");
  });
});
