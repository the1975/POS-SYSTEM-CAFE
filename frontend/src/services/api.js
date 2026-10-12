// Satu-satunya tempat yang tahu base URL & format error API.
// Saat dev, "/api/v1" diteruskan Vite ke backend (lihat vite.config.js).
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export class ApiError extends Error {
  constructor(status, code, message, details) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export async function apiFetch(path, { headers, ...options } = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    // Header bawaan digabung dengan header tambahan (mis. Idempotency-Key), bukan ditimpa.
    headers: { "Content-Type": "application/json", ...headers },
  });
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const err = body?.error;
    throw new ApiError(res.status, err?.code ?? "UNKNOWN", err?.message ?? "Terjadi kesalahan.", err?.details);
  }
  return body;
}

export const getHealth = () => apiFetch("/health");
