import { describe, it, expect } from "vitest";
import { markableItems } from "../src/features/kitchen/kitchen";

describe("Siap semua", () => {
  it("hanya item yang sedang dimasak atau remake yang ikut ditandai", () => {
    const order = {
      items: [
        { order_item_id: "a", status: "PREPARING" },
        { order_item_id: "b", status: "READY" },
        { order_item_id: "c", status: "REMAKE" },
        { order_item_id: "d", status: "PENDING" },
      ],
    };
    expect(markableItems(order).map((i) => i.order_item_id)).toEqual(["a", "c"]);
  });
});
