import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/apiClient.js";
import { getErrorMessage } from "../utils/errors.js";

export default function Register() {
  const nav = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    display_name: "",
  });
  const [err, setErr] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    try {
      const { data } = await api.post("/register/", form);
      const payload = data.success ? data.data : data;
      if (data.success === false) {
        setErr(data.message || "Registration failed.");
        return;
      }
      nav("/login", { replace: true, state: { registered: payload?.username } });
    } catch (ex) {
      setErr(getErrorMessage(ex));
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16">
      <h1 className="font-display text-3xl text-ink mb-2">Create account</h1>
      <p className="text-ink-muted text-sm mb-8">Join Spendly to track expenses and groups.</p>
      {err && (
        <div className="mb-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">{err}</div>
      )}
      <form onSubmit={onSubmit} className="space-y-4">
        {["username", "email", "display_name", "password"].map((field) => (
          <div key={field}>
            <label className="block text-xs font-medium text-ink-muted mb-1 capitalize">
              {field.replace("_", " ")}
            </label>
            <input
              type={field === "password" ? "password" : field === "email" ? "email" : "text"}
              className="w-full rounded-md border border-ink-muted/25 bg-paper px-3 py-2 text-sm"
              value={form[field]}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
              required={field !== "display_name"}
            />
          </div>
        ))}
        <button
          type="submit"
          className="w-full rounded-md bg-ink text-paper py-2.5 text-sm font-semibold hover:bg-accent transition-colors"
        >
          Register
        </button>
      </form>
      <p className="mt-6 text-sm text-ink-muted">
        Already have an account?{" "}
        <Link to="/login" className="text-accent font-medium">
          Sign in
        </Link>
      </p>
    </div>
  );
}
