import { describe, it, expect } from "vitest";
import {
  MAX_QUANTITY, cartCount, cartReducer, cartSubtotal, emptyCart, parseStoredCart,
} from "../src/stores/cart";

const teh = { id: "p1", name: "Es Teh", price: 8000 };
const nasi = { id: "p2", name: "Nasi Goreng", price: 25000 };
const add = (state, product) => cartReducer(state, { type: "add", product });

describe("cartReducer", () => {
  it("menambah produk baru dengan jumlah 1, dan menambah jumlah bila sudah ada", () => {
    let s = add(emptyCart, teh);
    expect(s.items).toEqual([{ productId: "p1", name: "Es Teh", price: 8000, quantity: 1 }]);
    s = add(s, teh);
    expect(s.items).toHaveLength(1);
    expect(s.items[0].quantity).toBe(2);
  });

  it("jumlah tidak melewati batas maksimum", () => {
    let s = add(emptyCart, teh);
    s = cartReducer(s, { type: "setQuantity", productId: "p1", quantity: 999 });
    expect(s.items[0].quantity).toBe(MAX_QUANTITY);
    s = add(s, teh);
    expect(s.items[0].quantity).toBe(MAX_QUANTITY);
  });

  it("jumlah 0 atau negatif menghapus item", () => {
    const s = add(add(emptyCart, teh), nasi);
    expect(cartReducer(s, { type: "setQuantity", productId: "p1", quantity: 0 }).items).toHaveLength(1);
    expect(cartReducer(s, { type: "setQuantity", productId: "p1", quantity: -3 }).items).toHaveLength(1);
  });

  it("remove, removeMany, dan clear", () => {
    const s = add(add(emptyCart, teh), nasi);
    expect(cartReducer(s, { type: "remove", productId: "p1" }).items.map((i) => i.productId)).toEqual(["p2"]);
    expect(cartReducer(s, { type: "removeMany", productIds: ["p1", "p2"] }).items).toEqual([]);
    expect(cartReducer(s, { type: "clear" })).toEqual(emptyCart);
  });

  it("menghitung jumlah item dan subtotal", () => {
    let s = add(add(emptyCart, teh), teh);
    s = add(s, nasi);
    expect(cartCount(s.items)).toBe(3);
    expect(cartSubtotal(s.items)).toBe(2 * 8000 + 25000);
  });
});

describe("parseStoredCart", () => {
  it("data kosong atau rusak menghasilkan keranjang kosong", () => {
    expect(parseStoredCart(null)).toEqual(emptyCart);
    expect(parseStoredCart("bukan json")).toEqual(emptyCart);
    expect(parseStoredCart('{"items":"salah"}')).toEqual(emptyCart);
  });

  it("hanya item valid yang dipakai (tanpa duplikat)", () => {
    const raw = JSON.stringify({
      items: [
        { productId: "p1", name: "Es Teh", price: 8000, quantity: 2 },
        { productId: "p1", name: "Es Teh", price: 8000, quantity: 5 }, // duplikat
        { productId: "p2", name: "Rusak", price: -1, quantity: 1 }, // harga negatif
        { productId: "p3", name: "Kebanyakan", price: 1000, quantity: 9999 },
        { productId: "p4", name: "Pecahan", price: 1000, quantity: 1.5 },
        { name: "Tanpa id", price: 1000, quantity: 1 },
      ],
    });
    const { items } = parseStoredCart(raw);
    expect(items).toEqual([{ productId: "p1", name: "Es Teh", price: 8000, quantity: 2 }]);
  });
});
