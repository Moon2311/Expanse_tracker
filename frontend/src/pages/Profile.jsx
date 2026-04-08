import { useEffect, useState } from "react";
import api from "../api/apiClient.js";
import { useAuth } from "../context/AuthContext.jsx";
import { getErrorMessage } from "../utils/errors.js";

export default function Profile() {
  const { setUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [displayName, setDisplayName] = useState("");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .get("/profile/")
      .then((res) => {
        setProfile(res.data);
        setDisplayName(res.data.display_name || "");
      })
      .catch((e) => setErr(getErrorMessage(e)));
  }, []);

  async function save(e) {
    e.preventDefault();
    setErr("");
    setMsg("");
    try {
      const { data } = await api.patch("/profile/", { display_name: displayName });
      setProfile(data);
      setUser(data);
      localStorage.setItem("user", JSON.stringify(data));
      setMsg("Profile updated.");
    } catch (e) {
      setErr(getErrorMessage(e));
    }
  }

  if (!profile) {
    return err ? <p className="text-red-600">{err}</p> : <p className="text-ink-muted">Loading…</p>;
  }

  return (
    <div className="max-w-lg">
      <h1 className="font-display text-3xl text-ink mb-2">Profile</h1>
      <p className="text-ink-muted text-sm mb-8">Username and email are fixed; you can edit your display name.</p>
      {msg && <p className="text-accent text-sm mb-4">{msg}</p>}
      {err && <p className="text-red-600 text-sm mb-4">{err}</p>}
      <dl className="space-y-3 text-sm mb-8">
        <div>
          <dt className="text-ink-faint">Username</dt>
          <dd className="font-medium">@{profile.username}</dd>
        </div>
        <div>
          <dt className="text-ink-faint">Email</dt>
          <dd className="font-medium">{profile.email}</dd>
        </div>
        <div>
          <dt className="text-ink-faint">Member since</dt>
          <dd className="font-medium">{profile.date_joined?.slice(0, 10)}</dd>
        </div>
      </dl>
      <form onSubmit={save} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-ink-muted mb-1">Display name</label>
          <input
            className="w-full max-w-md rounded-md border border-ink-muted/25 bg-paper px-3 py-2 text-sm"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>
        <button
          type="submit"
          className="rounded-md bg-ink text-paper px-5 py-2 text-sm font-semibold hover:bg-accent"
        >
          Save
        </button>
      </form>
    </div>
  );
}
