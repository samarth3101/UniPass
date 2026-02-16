"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setAuth } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"scanner" | "organizer" | "admin">("scanner");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const apiUrl = '/api';
      const res = await fetch(`${apiUrl}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          email,
          full_name: fullName || null,
          password, 
          role: role.toUpperCase() // Backend expects uppercase role values
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Signup failed");
      }

      const data = await res.json();
      // Auto-login after signup
      setAuth(data.access_token, data.user);
      router.replace("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h1>Create account</h1>
        <p className="subtitle">
          Get started with UniPass in seconds
        </p>

        <form onSubmit={handleSignup}>
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="text"
            placeholder="Full Name (optional)"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <select 
            value={role} 
            onChange={(e) => setRole(e.target.value as any)}
            style={{
              padding: "0.875rem",
              border: "1px solid #e2e8f0",
              borderRadius: "8px",
              fontSize: "1rem",
              marginTop: "1rem"
            }}
          >
            <option value="scanner">Scanner Operator</option>
            <option value="organizer">Event Organizer</option>
            <option value="admin">Admin</option>
          </select>

          {error && <p className="error">{error}</p>}

          <button disabled={loading}>
            {loading ? "Creating account..." : "Sign up"}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <a href="/login">Sign in</a>
        </div>
      </div>
    </div>
  );
}