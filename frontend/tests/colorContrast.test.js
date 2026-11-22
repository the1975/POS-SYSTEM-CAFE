import { readFileSync } from "node:fs";
import { describe, it, expect } from "vitest";

const css = readFileSync(new URL("../src/app/styles.css", import.meta.url), "utf8");
const start = css.indexOf(":root");
const root = css.slice(start, css.indexOf("}", start));

const token = (name) => {
  const m = root.match(new RegExp(`--${name}:\\s*(#[0-9a-fA-F]{6})`));
  if (!m) throw new Error(`token --${name} tidak ditemukan`);
  return m[1];
};
const stops = (name) => root.match(new RegExp(`--${name}:[^;]*`))[0].match(/#[0-9a-fA-F]{6}/g);

const lum = (hex) => {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const f = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};
const ratio = (a, b) => {
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

describe("standar warna: kontras WCAG AA (minimal 4,5:1)", () => {
  const AA = 4.5;
  it("teks utama dan redup terbaca di latar dan kartu", () => {
    for (const fg of ["text", "muted"]) {
      for (const bg of ["bg", "surface"]) {
        expect(ratio(token(fg), token(bg)), `${fg} di ${bg}`).toBeGreaterThanOrEqual(AA);
      }
    }
  });
  it("teks putih terbaca di atas aksen dan gradasinya", () => {
    expect(ratio(token("accent-text"), token("accent"))).toBeGreaterThanOrEqual(AA);
    for (const c of stops("accent-grad")) {
      expect(ratio(token("accent-text"), c), `gradasi ${c}`).toBeGreaterThanOrEqual(AA);
    }
    for (const c of stops("danger-grad")) {
      expect(ratio("#ffffff", c), `gradasi bahaya ${c}`).toBeGreaterThanOrEqual(AA);
    }
  });
  it("teks hijau di atas hijau muda dan merah bahaya di atas kartu terbaca", () => {
    expect(ratio(token("accent-strong"), token("tint-flat"))).toBeGreaterThanOrEqual(AA);
    expect(ratio(token("danger"), token("surface"))).toBeGreaterThanOrEqual(AA);
  });
});
