import Header from "../components/layout/Header";
import CartBar from "../features/cart/CartBar";
import CartPanel from "../features/cart/CartPanel";
import ActiveOrderCard from "../features/orders/ActiveOrderCard";
import CategoryTabs from "../features/menu/CategoryTabs";
import ProductList from "../features/menu/ProductList";
import SearchBox from "../features/menu/SearchBox";
import { useMenu } from "../features/menu/useMenu";
import { useCart } from "../stores/CartContext";

// Halaman menu customer: tanpa login, tanpa nomor meja (user-flow.md §3-4).
export default function MenuPage() {
  const menu = useMenu();
  const { count } = useCart();
  const hasNav = menu.categories.length > 0;
  return (
    <>
      <Header />
      {/* has-nav / has-bar: ruang di bawah agar konten terakhir tidak tertutup navbar dan bar keranjang */}
      <main className={`container${hasNav ? " has-nav" : ""}${count > 0 ? " has-bar" : ""}`}>
        <ActiveOrderCard />
        <section className="intro">
          <h1 className="intro__title">Mau makan apa hari ini?</h1>
        </section>
        <SearchBox value={menu.search} onChange={menu.setSearch} />
        <ProductList menu={menu} />
      </main>
      <CategoryTabs
        categories={menu.categories}
        activeId={menu.categoryId}
        onSelect={menu.setCategoryId}
      />
      <CartBar raised={hasNav} />
      <CartPanel />
    </>
  );
}
