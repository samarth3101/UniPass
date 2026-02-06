const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
    ...(options.headers || {}),
  };

  // Add Authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers,
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "API error");
  }

  return res.json();
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
   AUTH HELPERS
====================== */
export async function login(email: string, password: string) {
  return api.post("/auth/login", { email, password });
}

export async function signup(email: string, password: string) {
  return api.post("/auth/signup", { email, password });
}