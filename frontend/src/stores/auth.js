// Sesi staff disimpan di sessionStorage: hilang saat tab ditutup (lebih aman di perangkat bersama).
export const SESSION_KEY = "monster-cafe:staff:v1";

// Halaman awal tiap role (sesuai user-flow.md). Role tak dikenal = tidak punya halaman.
export const ROLE_HOME = {
  ADMIN: "/admin",
  CONTROLLER: "/controller",
  KITCHEN: "/dapur",
  CASHIER: "/kasir",
  PICKUP: "/pickup",
};

export const ROLE_LABEL = {
  ADMIN: "Admin",
  CONTROLLER: "Controller",
  KITCHEN: "Dapur",
  CASHIER: "Kasir",
  PICKUP: "Pickup",
};

export const homeForRole = (role) => ROLE_HOME[role] ?? null;

export function parseSession(raw) {
  try {
    const s = JSON.parse(raw);
    if (
      s &&
      typeof s.token === "string" && s.token &&
      s.user &&
      typeof s.user.name === "string" &&
      typeof s.user.role === "string"
    ) {
      return { token: s.token, user: { id: s.user.id, name: s.user.name, role: s.user.role } };
    }
  } catch {
    /* data rusak: anggap belum login */
  }
  return null;
}

export function loadSession(storage = window.sessionStorage) {
  try {
    return parseSession(storage.getItem(SESSION_KEY));
  } catch {
    return null;
  }
}

export function saveSession(session, storage = window.sessionStorage) {
  try {
    storage.setItem(SESSION_KEY, JSON.stringify(session));
  } catch {
    /* penyimpanan diblokir: sesi tetap jalan selama tab terbuka */
  }
}

export function clearSession(storage = window.sessionStorage) {
  try {
    storage.removeItem(SESSION_KEY);
  } catch {
    /* abaikan */
  }
}
