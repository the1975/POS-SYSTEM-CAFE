import { apiFetch } from "./api";

// Login staff: mengembalikan { data: { access_token, user: { id, name, role } } }.
export function login(email, password) {
  return apiFetch("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
}

// Cek token masih berlaku dan ambil role terbaru dari server.
export function getMe(token, { signal } = {}) {
  return apiFetch("/auth/me", { headers: { Authorization: `Bearer ${token}` }, signal });
}
