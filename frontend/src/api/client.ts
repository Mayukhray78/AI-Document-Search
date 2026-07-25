import axios from "axios";


const API_URL =
  import.meta.env.VITE_API_URL ??
  "http://127.0.0.1:8000";


const apiClient = axios.create({
  baseURL: API_URL,
});


apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});


apiClient.interceptors.response.use(
  (response) => response,

  (error) => {
    if (
      error.response?.status === 401 ||
      error.response?.status === 403
    ) {
      localStorage.removeItem("access_token");
    }

    return Promise.reject(error);
  },
);


export default apiClient;