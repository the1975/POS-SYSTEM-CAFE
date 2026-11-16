import { describe, it, expect } from "vitest";
import { groupBy } from "../src/features/admin/group";

describe("groupBy", () => {
  it("mengelompokkan item dan mempertahankan urutan kemunculan", () => {
    const items = [
      { id: 1, cat: "Minuman" },
      { id: 2, cat: "Makanan" },
      { id: 3, cat: "Minuman" },
    ];
    const groups = groupBy(items, (i) => i.cat);
    expect(groups.map((g) => [g.label, g.items.map((i) => i.id)])).toEqual([
      ["Minuman", [1, 3]],
      ["Makanan", [2]],
    ]);
  });

  it("kunci kosong masuk ke Lainnya dan daftar kosong menghasilkan array kosong", () => {
    expect(groupBy([], (i) => i.cat)).toEqual([]);
    expect(groupBy([{ cat: "" }], (i) => i.cat)[0].label).toBe("Lainnya");
  });
});
