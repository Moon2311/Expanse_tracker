import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "/api";

const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const access = localStorage.getItem("access");
  if (access) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh");
      if (refresh) {
        try {
          const { data } = await axios.post(`${baseURL}/token/refresh/`, {
            refresh,
          });
          localStorage.setItem("access", data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem("access");
          localStorage.removeItem("refresh");
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
