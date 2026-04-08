import { useEffect, useRef } from "react";

export function usePolling(callback, intervalMs, enabled = true) {
  const cb = useRef(callback);
  cb.current = callback;

  useEffect(() => {
    if (!enabled) return undefined;
    const id = setInterval(() => cb.current(), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs, enabled]);
}
