import { describe, it, expect, vi, afterEach } from "vitest";
import { apiFetch, ApiError } from "../src/services/api";

afterEach(() => vi.restoreAllMocks());

describe("apiFetch", () => {
  it("mengembalikan body saat sukses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ status: "ok" }) }));
    expect(await apiFetch("/health")).toEqual({ status: "ok" });
  });

  it("melempar ApiError dengan format error backend", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false, status: 409,
      json: async () => ({ error: { code: "CONFLICT", message: "Stok tidak cukup." } }),
    }));
    await expect(apiFetch("/x")).rejects.toMatchObject({ status: 409, code: "CONFLICT" });
    await expect(apiFetch("/x")).rejects.toBeInstanceOf(ApiError);
  });
});
