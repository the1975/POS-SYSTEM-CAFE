import { apiFetch } from "./api";

// Satu-satunya tempat yang tahu bentuk endpoint menu (/categories, /products).

export const PAGE_SIZE = 20;

export function getCategories({ signal } = {}) {
  return apiFetch("/categories", { signal });
}

export function getProducts({ categoryId, search, page = 1, pageSize = PAGE_SIZE, signal } = {}) {
  const params = new URLSearchParams();
  // Parameter kosong tidak dikirim, supaya URL bersih dan backend memakai defaultnya.
  if (categoryId) params.set("category_id", categoryId);
  if (search) params.set("search", search);
  params.set("page", String(page));
  params.set("page_size", String(pageSize));
  return apiFetch(`/products?${params.toString()}`, { signal });
}
