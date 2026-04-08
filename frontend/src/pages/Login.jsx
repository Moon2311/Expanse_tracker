import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { getErrorMessage } from "../utils/errors.js";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    try {
      await login(username.trim(), password);
      nav("/", { replace: true });
    } catch (ex) {
      setErr(getErrorMessage(ex));
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16">
      <h1 className="font-display text-3xl text-ink mb-2">Sign in</h1>
      <p className="text-ink-muted text-sm mb-8">Use your Spendly username and password.</p>
      {err && (
        <div className="mb-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">{err}</div>
      )}
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-ink-muted mb-1">Username</label>
          <input
            className="w-full rounded-md border border-ink-muted/25 bg-paper px-3 py-2 text-sm"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-ink-muted mb-1">Password</label>
          <input
            type="password"
            className="w-full rounded-md border border-ink-muted/25 bg-paper px-3 py-2 text-sm"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full rounded-md bg-ink text-paper py-2.5 text-sm font-semibold hover:bg-accent transition-colors"
        >
          Sign in
        </button>
      </form>
      <p className="mt-6 text-sm text-ink-muted">
        No account?{" "}
        <Link to="/register" className="text-accent font-medium">
          Register
        </Link>
      </p>
    </div>
  );
}
