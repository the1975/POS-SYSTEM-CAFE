import { useEffect, useState } from "react";
import { getHealth } from "../services/api";

// Placeholder Phase 1: cuma bukti frontend <-> backend nyambung.
// UI asli mengikuti docs/ui-ux/design-system.md di fase berikutnya.
export default function App() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    getHealth()
      .then(() => setStatus("ok"))
      .catch(() => setStatus("down"));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>Monster Café</h1>
      <p>Backend: {status === "checking" ? "memeriksa…" : status === "ok" ? "terhubung" : "tidak terhubung"}</p>
    </main>
  );
}
