import Header from "../components/layout/Header";
import CategoryTabs from "../features/menu/CategoryTabs";
import ProductList from "../features/menu/ProductList";
import SearchBox from "../features/menu/SearchBox";
import { useMenu } from "../features/menu/useMenu";

// Halaman menu customer: tanpa login, tanpa nomor meja (user-flow.md §3-4).
export default function MenuPage() {
  const menu = useMenu();
  return (
    <>
      <Header />
      <main className="container">
        <section className="intro">
          <h1 className="intro__title">Mau makan apa hari ini?</h1>
          <p className="muted">Pilih menunya, kami kabari saat pesananmu siap diambil.</p>
        </section>
        <SearchBox value={menu.search} onChange={menu.setSearch} />
        <CategoryTabs
          categories={menu.categories}
          activeId={menu.categoryId}
          onSelect={menu.setCategoryId}
        />
        <ProductList menu={menu} />
      </main>
    </>
  );
}
