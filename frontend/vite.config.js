import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Akses lewat alamat port Codespaces (*.app.github.dev) harus diizinkan.
    allowedHosts: [".app.github.dev"],
    // Saat dev, /api diteruskan ke backend FastAPI. Browser hanya bicara ke Vite (satu origin).
    proxy: { "/api": "http://localhost:8000" },
  },
});
