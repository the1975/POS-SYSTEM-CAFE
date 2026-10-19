import { ROLE_LABEL } from "../../stores/auth";

export const roleLabel = (name) => ROLE_LABEL[name] ?? name;

export const USER_STATUS_FILTERS = [
  { value: "", label: "Semua akun" },
  { value: "true", label: "Aktif" },
  { value: "false", label: "Nonaktif" },
];

// Aturan sama dengan backend (users/schema.py).
export const MIN_PASSWORD_LENGTH = 12;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
export const isEmailPlausible = (text) => EMAIL_RE.test(String(text ?? "").trim());
export const isPasswordValid = (text) => String(text ?? "").length >= MIN_PASSWORD_LENGTH;

export function isCreateFormValid(form) {
  return (
    form.name.trim().length > 0 &&
    isEmailPlausible(form.email) &&
    Boolean(form.roleId) &&
    isPasswordValid(form.password)
  );
}

// Hanya field yang berubah yang dikirim (backend menolak body kosong).
export function buildUserPatch(user, form) {
  const patch = {};
  const name = form.name.trim();
  if (name && name !== user.name) patch.name = name;
  if (form.roleId && form.roleId !== user.role_id) patch.role_id = form.roleId;
  if (form.isActive !== user.is_active) patch.is_active = form.isActive;
  return patch;
}

// Sandi acak tanpa huruf/angka yang mirip (0 O 1 l I) supaya mudah dibacakan atau diketik.
const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";

export function generatePassword(length = 16, fillRandom = (arr) => crypto.getRandomValues(arr)) {
  // Buang byte di atas batas agar setiap karakter peluangnya sama (tanpa bias modulo).
  const limit = Math.floor(256 / ALPHABET.length) * ALPHABET.length;
  let out = "";
  while (out.length < length) {
    for (const b of fillRandom(new Uint8Array(length * 2))) {
      if (b < limit && out.length < length) out += ALPHABET[b % ALPHABET.length];
    }
  }
  return out;
}

// Saat koneksi/server gagal hasilnya tidak pasti (akun bisa sudah terbuat): suruh cek daftar dulu.
export function describeUserError(err) {
  switch (err?.code) {
    case "EMAIL_ALREADY_USED":
      return "Email ini sudah dipakai akun lain.";
    case "ROLE_NOT_FOUND":
      return "Role tidak dikenal. Muat ulang halaman.";
    case "CANNOT_MODIFY_SELF":
      return "Kamu tidak bisa menonaktifkan atau mengganti role akunmu sendiri.";
    case "LAST_ADMIN":
      return "Harus tersisa minimal satu admin aktif.";
    case "USER_NOT_FOUND":
      return "Akun tidak ditemukan. Muat ulang daftar akun.";
    default:
  }
  if (err?.status === 403) return "Hanya admin yang boleh mengelola akun.";
  if (err?.status === 422) return "Periksa isian: nama wajib, email valid, sandi minimal 12 karakter.";
  return "Koneksi atau server bermasalah. Periksa daftar akun dulu sebelum mencoba lagi.";
}
