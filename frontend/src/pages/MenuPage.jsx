import Header from "../components/layout/Header";
import CartBar from "../features/cart/CartBar";
import CategoryTabs from "../features/menu/CategoryTabs";
import ProductList from "../features/menu/ProductList";
import SearchBox from "../features/menu/SearchBox";
import { useMenu } from "../features/menu/useMenu";
import { useCart } from "../stores/CartContext";

// Halaman menu customer: tanpa login, tanpa nomor meja (user-flow.md §3-4).
export default function MenuPage() {
  const menu = useMenu();
  const { count } = useCart();
  return (
    <>
      <Header />
      {/* has-bar: memberi ruang di bawah agar konten terakhir tidak tertutup bar keranjang */}
      <main className={`container${count > 0 ? " has-bar" : ""}`}>
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
      <CartBar />
    </>
  );
}
