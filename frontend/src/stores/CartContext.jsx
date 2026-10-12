import { createContext, useContext, useEffect, useMemo, useReducer } from "react";
import {
  STORAGE_KEY, cartCount, cartReducer, cartSubtotal, emptyCart, parseStoredCart,
} from "./cart";

const CartContext = createContext(null);

function loadInitialState() {
  try {
    return parseStoredCart(window.localStorage.getItem(STORAGE_KEY));
  } catch {
    return emptyCart; // localStorage diblokir (mis. mode privat): keranjang tetap jalan di memori
  }
}

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, undefined, loadInitialState);

  // Keranjang bertahan walau halaman di-refresh atau tak sengaja tertutup.
  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      /* abaikan: hanya gagal menyimpan, keranjang di layar tetap benar */
    }
  }, [state]);

  const value = useMemo(
    () => ({
      items: state.items,
      count: cartCount(state.items),
      subtotal: cartSubtotal(state.items),
      quantityOf: (id) => state.items.find((i) => i.productId === id)?.quantity ?? 0,
      add: (product) => dispatch({ type: "add", product }),
      setQuantity: (productId, quantity) => dispatch({ type: "setQuantity", productId, quantity }),
      remove: (productId) => dispatch({ type: "remove", productId }),
      removeMany: (productIds) => dispatch({ type: "removeMany", productIds }),
      clear: () => dispatch({ type: "clear" }),
    }),
    [state]
  );
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart harus dipakai di dalam <CartProvider>");
  return ctx;
}
