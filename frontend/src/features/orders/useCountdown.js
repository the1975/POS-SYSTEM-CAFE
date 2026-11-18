import { useEffect, useState } from "react";
import { secondsLeft } from "./countdown";

// Sisa detik yang berdetak tiap detik. null bila tidak ada batas waktu.
export function useCountdown(expiresAt) {
  const [left, setLeft] = useState(() => secondsLeft(expiresAt));
  useEffect(() => {
    setLeft(secondsLeft(expiresAt));
    if (!expiresAt) return undefined;
    const id = setInterval(() => setLeft(secondsLeft(expiresAt)), 1000);
    return () => clearInterval(id);
  }, [expiresAt]);
  return left;
}
