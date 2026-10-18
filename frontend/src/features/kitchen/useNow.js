import { useEffect, useState } from "react";

// Jam yang berdetak pelan supaya pewaktu kartu ikut bergerak tanpa memuat ulang data.
export function useNow(intervalMs = 30000) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return now;
}
