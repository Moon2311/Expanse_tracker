import { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../api/apiClient.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem("user");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const access = localStorage.getItem("access");
    if (!access) {
      setReady(true);
      return;
    }
    api
      .get("/profile/")
      .then((res) => {
        const u = res.data;
        setUser(u);
        localStorage.setItem("user", JSON.stringify(u));
      })
      .catch(() => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user");
        setUser(null);
      })
      .finally(() => setReady(true));
  }, []);

  const login = async (username, password) => {
    const { data } = await api.post("/login/", { username, password });
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user");
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      ready,
      isAuthenticated: !!user,
      login,
      logout,
      setUser,
    }),
    [user, ready]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside AuthProvider");
  return ctx;
}
