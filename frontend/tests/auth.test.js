import { describe, it, expect, vi, afterEach } from "vitest";
import { ApiError } from "../src/services/api";
import { getMe, login } from "../src/services/authApi";
import {
  SESSION_KEY,
  clearSession,
  homeForRole,
  loadSession,
  parseSession,
  saveSession,
} from "../src/stores/auth";
import { screensForRole } from "../src/features/staff/screens";
import { describeLoginError } from "../src/features/staff/errors";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: {} }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

function fakeStorage() {
  const data = {};
  return {
    data,
    getItem: (k) => data[k] ?? null,
    setItem: (k, v) => {
      data[k] = v;
    },
    removeItem: (k) => {
      delete data[k];
    },
  };
}

const SESSION = { token: "tkn-123", user: { id: "u1", name: "Sari", role: "CASHIER" } };

describe("authApi", () => {
  it("login mengirim email dan password ke /auth/login", async () => {
    const fn = mockFetch();
    await login("kasir@example.com", "rahasia");
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/auth/login");
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({ email: "kasir@example.com", password: "rahasia" });
  });

  it("getMe mengirim token lewat header Authorization", async () => {
    const fn = mockFetch();
    await getMe("tkn-123");
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/auth/me");
    expect(options.headers.Authorization).toBe("Bearer tkn-123");
    expect(url).not.toContain("tkn-123");
  });
});

describe("role dan layar", () => {
  it("tiap role punya halaman awal; role tak dikenal tidak", () => {
    expect(homeForRole("CASHIER")).toBe("/kasir");
    expect(homeForRole("KITCHEN")).toBe("/dapur");
    expect(homeForRole("PICKUP")).toBe("/pickup");
    expect(homeForRole("CONTROLLER")).toBe("/controller");
    expect(homeForRole("ADMIN")).toBe("/admin");
    expect(homeForRole("TUKANG_SULAP")).toBeNull();
  });

  it("layar yang boleh dibuka mengikuti aturan backend", () => {
    expect(screensForRole("CASHIER").map((s) => s.path)).toEqual(["/kasir"]);
    expect(screensForRole("KITCHEN").map((s) => s.path)).toEqual(["/dapur"]);
    expect(screensForRole("PICKUP").map((s) => s.path)).toEqual(["/pickup"]);
    expect(screensForRole("ADMIN")).toHaveLength(5);
  });
});

describe("sesi staff", () => {
  it("parseSession menerima sesi valid dan menolak data rusak", () => {
    expect(parseSession(JSON.stringify(SESSION))).toEqual(SESSION);
    expect(parseSession("bukan json")).toBeNull();
    expect(parseSession(null)).toBeNull();
    expect(parseSession(JSON.stringify({ token: "", user: SESSION.user }))).toBeNull();
    expect(parseSession(JSON.stringify({ token: "x", user: { name: "A" } }))).toBeNull();
  });

  it("simpan, muat, lalu hapus sesi", () => {
    const storage = fakeStorage();
    expect(loadSession(storage)).toBeNull();
    saveSession(SESSION, storage);
    expect(storage.data[SESSION_KEY]).toBeTruthy();
    expect(loadSession(storage)).toEqual(SESSION);
    clearSession(storage);
    expect(loadSession(storage)).toBeNull();
  });
});

describe("pesan error login", () => {
  it("memetakan status ke pesan yang jelas", () => {
    expect(describeLoginError(new ApiError(401, "UNAUTHORIZED", "x"))).toMatch(/salah/);
    expect(describeLoginError(new ApiError(422, "VALIDATION_ERROR", "x"))).toMatch(/Isi email/);
    expect(describeLoginError(new ApiError(500, "INTERNAL_ERROR", "x"))).toMatch(/Server/);
    expect(describeLoginError(new TypeError("Failed to fetch"))).toMatch(/terhubung/);
  });
});
