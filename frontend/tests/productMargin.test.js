import { describe, it, expect } from "vitest";
import { marginInfo } from "../src/features/admin/products";

describe("marginInfo", () => {
  it("menghitung laba dan persen dari harga jual dan modal", () => {
    expect(marginInfo({ price: "25000", costPrice: "15000" })).toEqual({ profit: 10000, percent: 40 });
  });
  it("rugi bila modal lebih besar dari harga jual", () => {
    expect(marginInfo({ price: "10000", costPrice: "12500" })).toEqual({ profit: -2500, percent: -25 });
  });
  it("kosong atau tidak valid menghasilkan null", () => {
    expect(marginInfo({ price: "", costPrice: "15000" })).toBeNull();
    expect(marginInfo({ price: "25000", costPrice: "" })).toBeNull();
    expect(marginInfo({ price: "0", costPrice: "0" })).toBeNull();
  });
});
