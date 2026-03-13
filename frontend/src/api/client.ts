/**
 * API Client - axios konfigūracija
 */

import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000, // 5 minutės AI generavimui (Gemini gali užtrukti)
});

// Request interceptor - galima pridėti auth token ateityje
apiClient.interceptors.request.use(
  (config) => {
    // const token = localStorage.getItem('token');
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor - error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || "Įvyko klaida";
    console.error("API Error:", message);
    return Promise.reject(error);
  },
);

export default apiClient;
