import { getApiUrl } from '@/config/api';

const API_BASE = getApiUrl();

/* ======================
   RAW FETCH WRAPPER
====================== */
async function request(
  path: string,
  options: RequestInit = {}
) {
  // Get token from localStorage
  const token = typeof window !== "undefined" 
    ? localStorage.getItem("unipass_token") 
    : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };

  // Add Authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      credentials: "include",
      headers,
      ...options,
    });

    if (!res.ok) {
      // Handle 401 Unauthorized - redirect to login
      if (res.status === 401) {
        if (typeof window !== "undefined") {
          localStorage.removeItem("unipass_token");
          localStorage.removeItem("unipass_user");
          window.location.href = "/login";
        }
        throw new Error("Session expired. Please login again.");
      }

      let errorMessage = "API error";
      
      try {
        const err = await res.json();
        errorMessage = err.detail || err.message || `HTTP ${res.status}: ${res.statusText}`;
      } catch {
        errorMessage = `HTTP ${res.status}: ${res.statusText}`;
      }
      
      throw new Error(errorMessage);
    }

    return res.json();
  } catch (error: any) {
    // Enhance error messages for common issues
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      throw new Error(
        'Unable to connect to the server. Please ensure:\n' +
        '1. The backend server is running\n' +
        '2. You have a stable internet connection\n' +
        '3. No firewall is blocking the connection'
      );
    }
    
    // Re-throw other errors as-is
    throw error;
  }
}

/* ======================
   DEFAULT API EXPORT
====================== */
const api = {
  get: (path: string) => request(path),
  post: (path: string, body?: any) =>
    request(path, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  put: (path: string, body?: any) =>
    request(path, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  delete: (path: string) =>
    request(path, {
      method: "DELETE",
    }),
};

export default api;

/* ======================
   HEALTH CHECK
====================== */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health/`, {
      method: 'GET',
      credentials: 'include',
    });
    return response.ok;
  } catch {
    return false;
  }
}

/* ======================
   AUTH HELPERS
====================== */
export async function login(email: string, password: string) {
  return api.post("/auth/login/", { email, password });
}

export async function signup(email: string, password: string) {
  return api.post("/auth/signup/", { email, password });
}