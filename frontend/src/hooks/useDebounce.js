import { useEffect, useState } from "react";

// Menunda nilai yang berubah cepat (mis. ketikan) supaya tidak menembak API tiap huruf.
export function useDebounce(value, delayMs = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer); // batalkan jika nilai berubah lagi sebelum waktunya
  }, [value, delayMs]);
  return debounced;
}
