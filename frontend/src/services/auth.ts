import axios from "axios";

const API_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const authService = {
  async register(data: any) {
    const response = await api.post("/auth/register", data);
    return response.data;
  },

  async login(data: any) {
    const params = new URLSearchParams();
    params.append("username", data.email);
    params.append("password", data.password);

    const response = await api.post("/auth/login", params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    if (response.data.access_token) {
      localStorage.setItem("token", response.data.access_token);
    }
    return response.data;
  },

  logout() {
    localStorage.removeItem("token");
  },

  async getProfile() {
    const response = await api.get("/auth/me");
    return response.data;
  },
};

export default api;
