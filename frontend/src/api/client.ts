/**
 * API Client - axios konfigūracija su autentifikacija
 */

import axios from "axios";
import { useAuthStore } from "@/stores/authStore";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000, // 5 minutės AI generavimui (Gemini gali užtrukti)
});

// Request interceptor - prideda Bearer token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor - error handling + auto-logout on 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token pasibaigė arba netinkamas — atsijungti
      const { logout } = useAuthStore.getState();
      logout();
      // Redirect į login (jei dar ne login puslapyje)
      if (window.location.pathname !== "/prisijungti") {
        window.location.href = "/prisijungti";
      }
    }
    const message = error.response?.data?.detail || "Įvyko klaida";
    console.error("API Error:", message);
    return Promise.reject(error);
  },
);

export default apiClient;
