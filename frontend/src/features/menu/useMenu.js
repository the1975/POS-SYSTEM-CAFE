import { useCallback, useEffect, useRef, useState } from "react";
import { useDebounce } from "../../hooks/useDebounce";
import { getCategories, getProducts } from "../../services/menuApi";

// Semua logika data halaman menu ada di sini; komponen hanya menampilkan hasilnya.
export function useMenu() {
  const [categories, setCategories] = useState([]);
  const [categoryId, setCategoryId] = useState(null); // null = semua kategori
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search.trim(), 300);

  const [items, setItems] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | ready | error
  const [loadingMore, setLoadingMore] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  // Penanda "generasi" pencarian: respons "muat lagi" yang datang terlambat
  // setelah filter berubah akan dibuang, bukan ditempelkan ke daftar baru.
  const generation = useRef(0);

  // Kategori cukup dimuat sekali. Kalau gagal, menu tetap bisa dipakai tanpa filter kategori.
  useEffect(() => {
    const controller = new AbortController();
    getCategories({ signal: controller.signal })
      .then((res) => setCategories(res.data))
      .catch(() => {});
    return () => controller.abort();
  }, []);

  // Setiap filter/pencarian berubah (atau user menekan "Coba lagi"), mulai ulang dari halaman 1.
  useEffect(() => {
    const controller = new AbortController();
    generation.current += 1;
    setStatus("loading");
    getProducts({ categoryId, search: debouncedSearch, page: 1, signal: controller.signal })
      .then((res) => {
        setItems(res.data);
        setPagination(res.pagination);
        setStatus("ready");
      })
      .catch((err) => {
        if (err.name !== "AbortError") setStatus("error");
      });
    return () => controller.abort(); // permintaan lama dibatalkan saat filter berubah
  }, [categoryId, debouncedSearch, reloadKey]);

  const hasMore = pagination ? pagination.page < pagination.total_pages : false;

  const loadMore = useCallback(async () => {
    if (!pagination || loadingMore || !hasMore) return;
    const myGeneration = generation.current;
    setLoadingMore(true);
    try {
      const res = await getProducts({
        categoryId,
        search: debouncedSearch,
        page: pagination.page + 1,
      });
      if (myGeneration !== generation.current) return; // filter sudah berganti
      setItems((prev) => [...prev, ...res.data]);
      setPagination(res.pagination);
    } catch {
      // Biarkan daftar yang sudah tampil; user bisa menekan tombolnya lagi.
    } finally {
      setLoadingMore(false);
    }
  }, [pagination, loadingMore, hasMore, categoryId, debouncedSearch]);

  const resetFilters = useCallback(() => {
    setSearch("");
    setCategoryId(null);
  }, []);

  return {
    categories, categoryId, setCategoryId,
    search, setSearch,
    items, status, hasMore, loadingMore, loadMore,
    reload: () => setReloadKey((k) => k + 1),
    resetFilters,
    hasFilters: Boolean(categoryId || search.trim()),
  };
}
