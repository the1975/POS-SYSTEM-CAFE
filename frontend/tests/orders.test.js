import { describe, it, expect, vi, afterEach } from "vitest";
import { ApiError } from "../src/services/api";
import { createOrder, getOrder } from "../src/services/orderApi";
import { describeCheckoutError } from "../src/features/checkout/errors";
import { addOrderAccess, parseOrderAccess } from "../src/stores/orderAccess";
import { statusLabel } from "../src/features/orders/statusLabels";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: {} }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("orderApi", () => {
  it("createOrder mengirim kunci idempotensi dan HANYA product_id + quantity", async () => {
    const fn = mockFetch();
    await createOrder(
      { customerName: "Leo", paymentMethod: "CASH", items: [{ product_id: "p1", quantity: 2 }] },
      "kunci-123456"
    );
    const [, options] = fn.mock.calls[0];
    expect(options.method).toBe("POST");
    expect(options.headers["Idempotency-Key"]).toBe("kunci-123456");
    expect(options.headers["Content-Type"]).toBe("application/json"); // tidak tertimpa
    expect(JSON.parse(options.body)).toEqual({
      customer_name: "Leo",
      payment_method: "CASH",
      items: [{ product_id: "p1", quantity: 2 }],
    });
  });

  it("getOrder mengirim token lewat header, bukan URL", async () => {
    const fn = mockFetch();
    await getOrder("order-1", "rahasia-token");
    const [url, options] = fn.mock.calls[0];
    expect(options.headers["X-Tracking-Token"]).toBe("rahasia-token");
    expect(url).not.toContain("rahasia-token");
  });
});

describe("describeCheckoutError", () => {
  const cart = [
    { productId: "p1", name: "Es Teh", price: 8000, quantity: 1 },
    { productId: "p2", name: "Nasi Goreng", price: 25000, quantity: 1 },
  ];

  it("menu tidak tersedia -> daftar item keranjang yang bermasalah", () => {
    const err = new ApiError(422, "INVALID_ORDER_ITEMS", "x", [
      { product_id: "p2", reason: "NOT_AVAILABLE" },
    ]);
    const d = describeCheckoutError(err, cart);
    expect(d.kind).toBe("unavailable");
    expect(d.unavailable.map((i) => i.name)).toEqual(["Nasi Goreng"]);
  });

  it("jumlah melebihi batas -> pesan dengan angka batas", () => {
    const err = new ApiError(422, "INVALID_ORDER_ITEMS", "x", [
      { product_id: "p1", reason: "QUANTITY_EXCEEDS_LIMIT", max_quantity: 20 },
    ]);
    expect(describeCheckoutError(err, cart).message).toContain("20");
  });

  it("error server dan jaringan menjelaskan bahwa aman diulang", () => {
    expect(describeCheckoutError(new ApiError(500, "INTERNAL_ERROR", "x"), cart).kind).toBe("server");
    const net = describeCheckoutError(new TypeError("Failed to fetch"), cart);
    expect(net.kind).toBe("network");
    expect(net.message).toContain("tidak akan terbuat dua kali");
  });

  it("error 4xx lain memakai pesan dari server", () => {
    const d = describeCheckoutError(new ApiError(409, "CONFLICT", "Bentrok."), cart);
    expect(d).toMatchObject({ kind: "other", message: "Bentrok." });
  });
});

describe("orderAccess", () => {
  const a = { orderId: "o1", orderNumber: "A001", token: "t1" };

  it("data rusak atau tidak lengkap dibuang", () => {
    expect(parseOrderAccess("bukan json")).toEqual([]);
    expect(parseOrderAccess(JSON.stringify([a, { orderId: "x" }, null]))).toEqual([a]);
  });

  it("pesanan terbaru di depan, duplikat diganti, dan dibatasi jumlahnya", () => {
    let list = [];
    for (let i = 1; i <= 12; i++) {
      list = addOrderAccess(list, { orderId: `o${i}`, orderNumber: `A${i}`, token: `t${i}` });
    }
    expect(list).toHaveLength(10);
    expect(list[0].orderId).toBe("o12");
    list = addOrderAccess(list, { orderId: "o5", orderNumber: "A5", token: "baru" });
    expect(list[0]).toMatchObject({ orderId: "o5", token: "baru" });
    expect(list.filter((o) => o.orderId === "o5")).toHaveLength(1);
  });
});

describe("statusLabel", () => {
  it("menerjemahkan status ke bahasa customer", () => {
    expect(statusLabel("PENDING")).toBe("Menunggu pembayaran");
    expect(statusLabel("READY")).toBe("Siap diambil");
    expect(statusLabel("TIDAK_ADA")).toBe("TIDAK_ADA");
  });
});
