import { Link } from "react-router-dom";
import Header from "../components/layout/Header";

export default function NotFoundPage() {
  return (
    <>
      <Header />
      <main className="container">
        <div className="state">
          <h1 className="state__title">Halaman tidak ditemukan.</h1>
          <p className="muted">Alamatnya mungkin salah, atau halamannya belum tersedia.</p>
          <Link to="/" className="btn">
            Kembali ke menu
          </Link>
        </div>
      </main>
    </>
  );
}
