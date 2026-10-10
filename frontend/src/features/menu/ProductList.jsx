import { EmptyState, ErrorState, LoadingList } from "../../components/feedback/States";
import ProductItem from "./ProductItem";

// Mengelompokkan produk per kategori (urutan dari API dipertahankan) agar menu terbaca
// seperti buku menu. Saat user memfilter satu kategori, judul grup tidak ditampilkan.
function groupByCategory(items, categories, showHeadings) {
  const names = new Map(categories.map((c) => [c.id, c.name]));
  const groups = [];
  for (const product of items) {
    const last = groups[groups.length - 1];
    if (last && last.id === product.category_id) {
      last.items.push(product);
    } else {
      groups.push({
        id: product.category_id,
        title: showHeadings ? names.get(product.category_id) : null,
        items: [product],
      });
    }
  }
  return groups;
}

export default function ProductList({ menu }) {
  const { status, items, categories, categoryId, hasFilters } = menu;

  if (status === "loading") return <LoadingList />;
  if (status === "error") return <ErrorState onRetry={menu.reload} />;
  if (items.length === 0) {
    return hasFilters ? (
      <EmptyState
        title="Menu tidak ditemukan."
        hint="Coba kata kunci lain, atau tampilkan semua menu."
        actionLabel="Tampilkan semua menu"
        onAction={menu.resetFilters}
      />
    ) : (
      <EmptyState
        title="Menu belum tersedia."
        hint="Silakan kembali lagi sebentar lagi."
      />
    );
  }

  const groups = groupByCategory(items, categories, categoryId === null);
  return (
    <div>
      {groups.map((group, i) => (
        <section key={`${group.id}-${i}`} className="group">
          {group.title && <h2 className="group__title">{group.title}</h2>}
          <ul className="list">
            {group.items.map((p) => (
              <ProductItem key={p.id} product={p} />
            ))}
          </ul>
        </section>
      ))}
      {menu.hasMore && (
        <button
          type="button"
          className="btn btn--block"
          onClick={menu.loadMore}
          disabled={menu.loadingMore}
        >
          {menu.loadingMore ? "Memuat…" : "Tampilkan lebih banyak"}
        </button>
      )}
    </div>
  );
}
