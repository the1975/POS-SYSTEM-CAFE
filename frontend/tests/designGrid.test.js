import { readFileSync } from "node:fs";
import { describe, it, expect } from "vitest";

const css = readFileSync(new URL("../src/app/styles.css", import.meta.url), "utf8");
const PROPS =
  /(?<![\w-])(?:padding|margin|gap|row-gap|column-gap|top|right|bottom|left|width|height|min-height|min-width|max-height)(?:-(?:top|right|bottom|left))?\s*:\s*([^;{}]+)/g;

describe("standar desain: grid 4px", () => {
  it("ukuran px di padding, margin, gap, dan dimensi kelipatan 4 (garis 1-2px dikecualikan)", () => {
    const bad = [];
    for (const m of css.matchAll(PROPS)) {
      for (const n of m[1].matchAll(/(?<![\w.])(\d+)px/g)) {
        const px = Number(n[1]);
        if (px > 2 && px % 4 !== 0) bad.push(`${m[0].trim()} -> ${px}px`);
      }
    }
    expect(bad).toEqual([]);
  });

  it("tab segmen punya tinggi sentuh minimal 44px", () => {
    const m = css.match(/\.seg__item\s*\{[^}]*min-height:\s*(\d+)px/);
    expect(Number(m[1])).toBeGreaterThanOrEqual(44);
  });
});
