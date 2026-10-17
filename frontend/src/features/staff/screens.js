// Role di sini sama dengan aturan backend (kitchen, pickup, payments). Frontend hanya
// menyembunyikan; otorisasi sebenarnya tetap di backend.
export const STAFF_SCREENS = [
  { path: "/kasir", title: "Kasir", roles: ["CASHIER", "ADMIN"], hint: "Antrean pembayaran dan konfirmasi uang tunai." },
  { path: "/dapur", title: "Dapur", roles: ["KITCHEN", "CONTROLLER", "ADMIN"], hint: "Antrean masak, tandai siap, dan buat ulang item." },
  { path: "/pickup", title: "Pickup", roles: ["PICKUP", "CONTROLLER", "ADMIN"], hint: "Verifikasi kode dan serah terima pesanan." },
  { path: "/controller", title: "Controller", roles: ["CONTROLLER", "ADMIN"], hint: "Pantau order dan tangani kendala." },
  { path: "/admin", title: "Admin", roles: ["ADMIN"], hint: "Order, produk, stok, analitik, dan pengguna." },
];

export const screensForRole = (role) => STAFF_SCREENS.filter((s) => s.roles.includes(role));
