import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getMe, login as loginRequest } from "../services/authApi";
import { clearSession, loadSession, saveSession } from "./auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => loadSession());

  // Token tersimpan bisa sudah kedaluwarsa atau akunnya dinonaktifkan: cek sekali saat dibuka.
  useEffect(() => {
    if (!session) return undefined;
    const controller = new AbortController();
    getMe(session.token, { signal: controller.signal })
      .then(({ data }) => {
        const next = { token: session.token, user: data }; // role terbaru dari server
        saveSession(next);
        setSession(next);
      })
      .catch((err) => {
        if (err?.status === 401) {
          clearSession();
          setSession(null);
        }
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(async (email, password) => {
    const { data } = await loginRequest(email, password);
    const next = { token: data.access_token, user: data.user };
    saveSession(next);
    setSession(next);
    return next;
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setSession(null);
  }, []);

  const value = useMemo(
    () => ({ user: session?.user ?? null, token: session?.token ?? null, login, logout }),
    [session, login, logout]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth harus dipakai di dalam AuthProvider");
  return ctx;
}
