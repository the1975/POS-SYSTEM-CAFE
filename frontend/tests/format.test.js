import { describe, it, expect } from "vitest";
import { formatRupiah } from "../src/utils/format";

describe("formatRupiah", () => {
  it("memberi titik pemisah ribuan tanpa spasi", () => {
    expect(formatRupiah(25000)).toBe("Rp25.000");
    expect(formatRupiah(1500000)).toBe("Rp1.500.000");
  });

  it("menangani nol, angka kecil, dan nilai tidak valid", () => {
    expect(formatRupiah(0)).toBe("Rp0");
    expect(formatRupiah(500)).toBe("Rp500");
    expect(formatRupiah(undefined)).toBe("Rp0");
  });
});
