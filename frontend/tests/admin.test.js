import { describe, it, expect, vi, afterEach } from "vitest";
import { ApiError } from "../src/services/api";
import { listStaffOrders, refundPayment } from "../src/services/staffApi";
import {
  ADMIN_TABS,
  ORDER_STATUS_LABELS,
  PAYMENT_FILTERS,
  PAYMENT_STATUS_LABELS,
  STATUS_FILTERS,
  canRefund,
  formatShortDateTime,
  isReasonValid,
  orderStatusLabel,
  pageInfo,
  paymentStatusLabel,
} from "../src/features/admin/admin";
import { describeRefundError } from "../src/features/admin/errors";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("adminApi", () => {
  it("listStaffOrders mengirim status, status bayar, pencarian, dan halaman", async () => {
    const fn = mockFetch();
    await listStaffOrders("tkn-1", { status: "CONFIRMED", paymentStatus: "PAID", search: "A1", page: 3, pageSize: 20 });
    const url = fn.mock.calls[0][0];
    expect(url).toContain("status=CONFIRMED");
    expect(url).toContain("payment_status=PAID");
    expect(url).toContain("search=A1");
    expect(url).toContain("page=3");
    expect(url).toContain("page_size=20");
  });

  it("listStaffOrders tanpa filter hanya mengirim halaman 1", async () => {
    const fn = mockFetch();
    await listStaffOrders("tkn-1");
    const url = fn.mock.calls[0][0];
    expect(url).toContain("page=1");
    expect(url).not.toContain("status=");
    expect(url).not.toContain("search=");
  });

  it("refundPayment mengirim jumlah (teks) dan alasan yang sudah dirapikan", async () => {
    const fn = mockFetch();
    await refundPayment("tkn-1", "pay-9", { amount: 17600, reason: "  Menu habis  " });
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/payments/pay-9/refund");
    expect(options.method).toBe("POST");
    expect(options.headers.Authorization).toBe("Bearer tkn-1");
    expect(JSON.parse(options.body)).toEqual({ amount: "17600", reason: "Menu habis" });
  });
});

describe("aturan tombol refund", () => {
  const base = { payment_id: "p1", payment_method: "CASH", payment_status: "PAID", status: "CONFIRMED" };

  it("hanya tunai, lunas, dan belum dimasak", () => {
    expect(canRefund(base)).toBe(true);
    expect(canRefund({ ...base, payment_method: "QRIS" })).toBe(false);
    expect(canRefund({ ...base, payment_status: "WAITING_CASH" })).toBe(false);
    expect(canRefund({ ...base, payment_status: "REFUNDED" })).toBe(false);
    expect(canRefund({ ...base, status: "PREPARING" })).toBe(false);
    expect(canRefund({ ...base, status: "READY" })).toBe(false);
    expect(canRefund({ ...base, payment_id: null })).toBe(false);
  });

  it("alasan minimal 3 karakter setelah dirapikan", () => {
    expect(isReasonValid("  ab  ")).toBe(false);
    expect(isReasonValid("abc")).toBe(true);
    expect(isReasonValid(null)).toBe(false);
  });
});

describe("label dan filter", () => {
  it("semua status resmi punya label, status tak dikenal tampil apa adanya", () => {
    const orderStatuses = ["PENDING", "CONFIRMED", "PREPARING", "READY", "OVERDUE", "COMPLETED", "CANCELLED"];
    for (const s of orderStatuses) expect(ORDER_STATUS_LABELS[s]).toBeTruthy();
    const paymentStatuses = ["PENDING", "WAITING_CASH", "PAID", "FAILED", "REFUND_REQUESTED", "REFUND_PENDING", "REFUNDED", "REFUND_FAILED"];
    for (const s of paymentStatuses) expect(PAYMENT_STATUS_LABELS[s]).toBeTruthy();
    expect(orderStatusLabel("APA_INI")).toBe("APA_INI");
    expect(paymentStatusLabel(null)).toBe("Belum ada pembayaran");
    expect(paymentStatusLabel("PAID")).toBe("Lunas");
  });

  it("pilihan filter diawali 'Semua' dengan nilai kosong", () => {
    expect(STATUS_FILTERS[0]).toEqual({ value: "", label: "Semua status order" });
    expect(PAYMENT_FILTERS[0].value).toBe("");
    expect(STATUS_FILTERS).toHaveLength(8);
    expect(PAYMENT_FILTERS).toHaveLength(9);
  });

  it("hanya tab Order yang siap", () => {
    expect(ADMIN_TABS.filter((t) => t.ready).map((t) => t.id)).toEqual(["orders", "users"]);
  });
});

describe("halaman dan waktu", () => {
  it("pageInfo", () => {
    expect(pageInfo(null)).toEqual({ hasPrev: false, hasNext: false, label: "" });
    expect(pageInfo({ page: 1, page_size: 20, total: 0, total_pages: 0 }).label).toBe("");
    const p = pageInfo({ page: 2, page_size: 20, total: 45, total_pages: 3 });
    expect(p).toEqual({ hasPrev: true, hasNext: true, label: "Halaman 2 dari 3 · 45 order" });
    expect(pageInfo({ page: 3, page_size: 20, total: 45, total_pages: 3 }).hasNext).toBe(false);
    expect(pageInfo({ page: 1, page_size: 20, total: 5, total_pages: 1 }).hasPrev).toBe(false);
  });

  it("formatShortDateTime", () => {
    expect(formatShortDateTime(new Date(2026, 9, 18, 14, 5).toISOString())).toBe("18 Okt 14.05");
    expect(formatShortDateTime(new Date(2026, 0, 3, 9, 7).toISOString())).toBe("3 Jan 09.07");
    expect(formatShortDateTime(null)).toBe("—");
    expect(formatShortDateTime("bukan tanggal")).toBe("—");
  });
});

describe("pesan error refund", () => {
  it("memetakan kode backend ke pesan yang jelas", () => {
    expect(describeRefundError(new ApiError(403, "FORBIDDEN", "x"))).toMatch(/Hanya admin/);
    expect(describeRefundError(new ApiError(409, "REFUND_NOT_ALLOWED", "Pembayaran ini sudah direfund."))).toBe("Pembayaran ini sudah direfund.");
    expect(describeRefundError(new ApiError(422, "REFUND_AMOUNT_INVALID", "x"))).toMatch(/sama dengan total/);
    expect(describeRefundError(new ApiError(422, "VALIDATION_ERROR", "x"))).toMatch(/alasan/);
  });

  it("gagal jaringan/server menyuruh periksa daftar dulu", () => {
    expect(describeRefundError(new TypeError("Failed to fetch"))).toMatch(/Periksa daftar order/);
    expect(describeRefundError(new ApiError(500, "INTERNAL_ERROR", "x"))).toMatch(/Periksa daftar order/);
  });
});
