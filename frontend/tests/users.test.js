import { describe, it, expect, vi, afterEach } from "vitest";
import { ApiError } from "../src/services/api";
import { createUser, listRoles, listUsers, updateUser } from "../src/services/staffApi";
import { pageInfo } from "../src/features/admin/admin";
import {
  MIN_PASSWORD_LENGTH,
  buildUserPatch,
  describeUserError,
  generatePassword,
  isCreateFormValid,
  isEmailPlausible,
  isPasswordValid,
  roleLabel,
} from "../src/features/admin/users";

afterEach(() => vi.unstubAllGlobals());

function mockFetch() {
  const fn = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("usersApi", () => {
  it("listUsers mengirim filter role, status, pencarian, dan halaman", async () => {
    const fn = mockFetch();
    await listUsers("tkn-1", { roleId: "r1", isActive: "false", search: "dapur", page: 2 });
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/users?");
    expect(url).toContain("role_id=r1");
    expect(url).toContain("is_active=false");
    expect(url).toContain("search=dapur");
    expect(url).toContain("page=2");
    expect(options.headers.Authorization).toBe("Bearer tkn-1");
  });

  it("listUsers tanpa filter tidak mengirim parameter kosong", async () => {
    const fn = mockFetch();
    await listUsers("tkn-1", { roleId: "", isActive: "", search: "" });
    const url = fn.mock.calls[0][0];
    expect(url).not.toContain("role_id=");
    expect(url).not.toContain("is_active=");
    expect(url).not.toContain("search=");
  });

  it("listRoles memakai /users/roles", async () => {
    const fn = mockFetch();
    await listRoles("tkn-1");
    expect(fn.mock.calls[0][0]).toContain("/users/roles");
  });

  it("createUser mengirim role_id dan merapikan nama/email", async () => {
    const fn = mockFetch();
    await createUser("tkn-1", { name: "  Sari ", email: " sari@x.com ", password: "rahasia-12345", roleId: "r9" });
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/users");
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({
      name: "Sari",
      email: "sari@x.com",
      password: "rahasia-12345",
      role_id: "r9",
    });
  });

  it("updateUser memakai PATCH ke /users/{id} dengan body patch", async () => {
    const fn = mockFetch();
    await updateUser("tkn-1", "u-5", { is_active: false });
    const [url, options] = fn.mock.calls[0];
    expect(url).toContain("/users/u-5");
    expect(options.method).toBe("PATCH");
    expect(JSON.parse(options.body)).toEqual({ is_active: false });
  });
});

describe("validasi form", () => {
  it("email dan sandi mengikuti aturan backend", () => {
    expect(isEmailPlausible("a@b.co")).toBe(true);
    expect(isEmailPlausible(" a@b.co ")).toBe(true);
    expect(isEmailPlausible("bukan-email")).toBe(false);
    expect(isEmailPlausible("a@b")).toBe(false);
    expect(MIN_PASSWORD_LENGTH).toBe(12);
    expect(isPasswordValid("x".repeat(12))).toBe(true);
    expect(isPasswordValid("x".repeat(11))).toBe(false);
  });

  it("isCreateFormValid butuh semua isian", () => {
    const ok = { name: "Sari", email: "sari@x.com", roleId: "r1", password: "x".repeat(12) };
    expect(isCreateFormValid(ok)).toBe(true);
    expect(isCreateFormValid({ ...ok, name: "  " })).toBe(false);
    expect(isCreateFormValid({ ...ok, email: "salah" })).toBe(false);
    expect(isCreateFormValid({ ...ok, roleId: "" })).toBe(false);
    expect(isCreateFormValid({ ...ok, password: "pendek" })).toBe(false);
  });

  it("buildUserPatch hanya berisi field yang berubah", () => {
    const user = { name: "Sari", role_id: "r1", is_active: true };
    expect(buildUserPatch(user, { name: "Sari", roleId: "r1", isActive: true })).toEqual({});
    expect(buildUserPatch(user, { name: "  Sari  ", roleId: "r1", isActive: true })).toEqual({});
    expect(buildUserPatch(user, { name: "Sari B", roleId: "r2", isActive: false })).toEqual({
      name: "Sari B",
      role_id: "r2",
      is_active: false,
    });
    expect(buildUserPatch(user, { name: "", roleId: "r1", isActive: true })).toEqual({});
  });
});

describe("sandi acak", () => {
  it("panjang sesuai, hanya karakter yang tidak mirip, dan deterministik dengan sumber acak palsu", () => {
    const fill = (arr) => arr.map((_, i) => i);
    expect(generatePassword(16, fill)).toBe("ABCDEFGHJKLMNPQR");
  });

  it("byte di atas batas dibuang (tanpa bias)", () => {
    let calls = 0;
    const fill = (arr) => {
      calls += 1;
      return calls === 1 ? arr.fill(250) : arr.fill(0);
    };
    expect(generatePassword(16, fill)).toBe("A".repeat(16));
    expect(calls).toBe(2);
  });

  it("sumber acak bawaan menghasilkan sandi yang lolos aturan backend", () => {
    if (!globalThis.crypto?.getRandomValues) return;
    const a = generatePassword();
    expect(a).toHaveLength(16);
    expect(a).toMatch(/^[A-HJ-NP-Za-km-np-z2-9]+$/);
    expect(isPasswordValid(a)).toBe(true);
    expect(generatePassword()).not.toBe(a);
  });
});

describe("pesan dan label", () => {
  it("memetakan kode backend ke pesan yang jelas", () => {
    expect(describeUserError(new ApiError(409, "EMAIL_ALREADY_USED", "x"))).toMatch(/sudah dipakai/);
    expect(describeUserError(new ApiError(409, "CANNOT_MODIFY_SELF", "x"))).toMatch(/akunmu sendiri/);
    expect(describeUserError(new ApiError(409, "LAST_ADMIN", "x"))).toMatch(/minimal satu admin/);
    expect(describeUserError(new ApiError(404, "USER_NOT_FOUND", "x"))).toMatch(/tidak ditemukan/);
    expect(describeUserError(new ApiError(403, "FORBIDDEN", "x"))).toMatch(/Hanya admin/);
    expect(describeUserError(new ApiError(422, "VALIDATION_ERROR", "x"))).toMatch(/Periksa isian/);
    expect(describeUserError(new TypeError("Failed to fetch"))).toMatch(/Periksa daftar akun/);
  });

  it("roleLabel dan label halaman 'akun'", () => {
    expect(roleLabel("CASHIER")).toBe("Kasir");
    expect(roleLabel("KITCHEN")).toBe("Dapur");
    expect(roleLabel("ENTAH")).toBe("ENTAH");
    expect(pageInfo({ page: 1, page_size: 20, total: 7, total_pages: 1 }, "akun").label).toBe(
      "Halaman 1 dari 1 · 7 akun"
    );
  });
});
