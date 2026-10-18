import { describe, it, expect, vi, afterEach } from "vitest";
import { ApiError } from "../src/services/api";
import { completePickup, listPickupOrders, verifyPickup } from "../src/services/staffApi";
import {
  PICKUP_STATUSES,
  cleanToken,
  isPlausibleToken,
  itemCount,
  orderFromRow,
  sortByReadyAt,
} from "../src/features/pickup/pickup";
import { describePickupError } from "../src/features/pickup/errors";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

const TOKEN_43 = "aB3_-xYz9QwErTyUiOpLkJhGfDsAzXcVbNm12345678";

describe("pickupApi", () => {
  it("listPickupOrders memfilter status dan memakai token lewat header", async () => {
    const fn = mockFetch();
    await listPickupOrders("tkn-1", "OVERDUE");
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/pickup/orders?");
    expect(url).toContain("status=OVERDUE");
    expect(url).not.toContain("tkn-1");
    expect(options.headers.Authorization).toBe("Bearer tkn-1");
  });

  it("verifyPickup mengirim token pickup lewat body, bukan URL", async () => {
    const fn = mockFetch();
    await verifyPickup("tkn-1", TOKEN_43);
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/pickup/verify");
    expect(url).not.toContain(TOKEN_43);
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({ pickup_token: TOKEN_43 });
  });

  it("completePickup memakai POST ke /pickup/{id}/complete", async () => {
    const fn = mockFetch();
    await completePickup("tkn-1", "p-9");
    expect(fn.mock.calls[0][0]).toContain("/pickup/p-9/complete");
    expect(fn.mock.calls[0][1].method).toBe("POST");
  });
});

describe("logika pickup", () => {
  it("READY dan OVERDUE sama-sama bisa diambil", () => {
    expect(PICKUP_STATUSES).toEqual(["READY", "OVERDUE"]);
  });

  it("isPlausibleToken menerima token asli dan menolak sampah", () => {
    expect(isPlausibleToken(TOKEN_43)).toBe(true);
    expect(isPlausibleToken(`  ${TOKEN_43}\n`)).toBe(true);
    expect(cleanToken(`  ${TOKEN_43}\n`)).toBe(TOKEN_43);
    expect(isPlausibleToken("pendek")).toBe(false);
    expect(isPlausibleToken("ada spasi di tengah token ini ya")).toBe(false);
    expect(isPlausibleToken("https://contoh.com/?a=1")).toBe(false);
    expect(isPlausibleToken("")).toBe(false);
    expect(isPlausibleToken(null)).toBe(false);
  });

  it("itemCount menjumlah semua kuantitas", () => {
    expect(itemCount([{ quantity: 2 }, { quantity: 1 }])).toBe(3);
    expect(itemCount([])).toBe(0);
    expect(itemCount(undefined)).toBe(0);
  });

  it("sortByReadyAt: paling lama siap di atas, tanpa waktu di bawah", () => {
    const a = { id: "a", ready_at: "2026-10-18T10:05:00Z" };
    const b = { id: "b", ready_at: "2026-10-18T09:50:00Z" };
    const c = { id: "c", ready_at: null };
    expect(sortByReadyAt([c, a, b]).map((o) => o.id)).toEqual(["b", "a", "c"]);
  });

  it("orderFromRow membentuk data panel dari baris daftar", () => {
    const row = { pickup_id: "p1", order_number: "A1", customer_name: "Leo", status: "READY", items: [{ name: "Es Teh", quantity: 1 }], verified: true };
    expect(orderFromRow(row)).toEqual({
      pickup_id: "p1",
      order_number: "A1",
      customer_name: "Leo",
      status: "READY",
      payment_status: null,
      items: [{ name: "Es Teh", quantity: 1 }],
    });
  });
});

describe("pesan error pickup", () => {
  it("token salah dan sudah diambil sesuai wireframe", () => {
    expect(describePickupError(new ApiError(404, "PICKUP_NOT_FOUND", "x")).message).toMatch(/tidak valid/);
    expect(describePickupError(new ApiError(409, "PICKUP_ALREADY_COMPLETED", "x")).message).toMatch(/sudah diambil/);
    expect(describePickupError(new ApiError(409, "PICKUP_INVALID_STATE", "x")).message).toMatch(/tidak mengizinkan/);
    expect(describePickupError(new ApiError(403, "FORBIDDEN", "x")).message).toMatch(/tidak boleh/);
  });

  it("gagal jaringan/server menyuruh periksa daftar dulu", () => {
    expect(describePickupError(new TypeError("Failed to fetch")).message).toMatch(/Periksa daftar/);
    expect(describePickupError(new ApiError(500, "INTERNAL_ERROR", "x")).message).toMatch(/Periksa daftar/);
  });
});
