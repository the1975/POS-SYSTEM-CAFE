// Logika keranjang (murni, tanpa React) supaya mudah diuji.
// PENTING: harga di keranjang HANYA untuk tampilan. Total sebenarnya selalu dihitung
// ulang oleh backend dari harga di database saat pesanan dibuat.

export const MAX_QUANTITY = 20; // cermin batas backend; yang menentukan tetap backend
export const STORAGE_KEY = "monster-cafe:cart:v1";
export const emptyCart = { items: [] };

const clamp = (n) => Math.max(0, Math.min(MAX_QUANTITY, Math.floor(n)));

function withQuantity(state, productId, quantity) {
  const q = clamp(quantity);
  if (q <= 0) return { items: state.items.filter((i) => i.productId !== productId) };
  return {
    items: state.items.map((i) => (i.productId === productId ? { ...i, quantity: q } : i)),
  };
}

export function cartReducer(state, action) {
  switch (action.type) {
    case "add": {
      const { product } = action;
      const existing = state.items.find((i) => i.productId === product.id);
      if (existing) return withQuantity(state, product.id, existing.quantity + 1);
      const item = {
        productId: product.id,
        name: product.name,
        price: Number(product.price),
        quantity: 1,
      };
      return { items: [...state.items, item] };
    }
    case "setQuantity":
      return withQuantity(state, action.productId, action.quantity);
    case "remove":
      return { items: state.items.filter((i) => i.productId !== action.productId) };
    case "removeMany": {
      const ids = new Set(action.productIds);
      return { items: state.items.filter((i) => !ids.has(i.productId)) };
    }
    case "clear":
      return emptyCart;
    default:
      return state;
  }
}

export const cartCount = (items) => items.reduce((sum, i) => sum + i.quantity, 0);
export const cartSubtotal = (items) => items.reduce((sum, i) => sum + i.price * i.quantity, 0);

// Data dari localStorage bisa rusak atau diubah manual. Hanya item yang valid yang dipakai.
export function parseStoredCart(raw) {
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || !Array.isArray(parsed.items)) return emptyCart;
    const seen = new Set();
    const items = [];
    for (const i of parsed.items) {
      const valid =
        i &&
        typeof i.productId === "string" &&
        i.productId.length > 0 &&
        typeof i.name === "string" &&
        Number.isFinite(i.price) &&
        i.price >= 0 &&
        Number.isInteger(i.quantity) &&
        i.quantity >= 1 &&
        i.quantity <= MAX_QUANTITY;
      if (valid && !seen.has(i.productId)) {
        seen.add(i.productId);
        items.push({ productId: i.productId, name: i.name, price: i.price, quantity: i.quantity });
      }
    }
    return { items };
  } catch {
    return emptyCart;
  }
}
