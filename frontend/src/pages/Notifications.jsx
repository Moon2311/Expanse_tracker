import { useEffect, useState } from "react";
import api from "../api/apiClient.js";
import { getErrorMessage } from "../utils/errors.js";

export default function Notifications() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  function load() {
    api
      .get("/notifications/")
      .then((r) => setItems(Array.isArray(r.data) ? r.data : []))
      .catch((e) => setErr(getErrorMessage(e)));
  }

  useEffect(() => {
    load();
  }, []);

  async function markAll() {
    try {
      await api.post("/notifications/mark-all-read/");
      load();
    } catch (e) {
      setErr(getErrorMessage(e));
    }
  }

  async function markOne(id) {
    try {
      await api.post(`/notifications/${id}/mark-read/`);
      load();
    } catch (e) {
      setErr(getErrorMessage(e));
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <h1 className="font-display text-3xl text-ink">Notifications</h1>
        <button
          type="button"
          onClick={markAll}
          className="text-sm font-medium text-accent bg-transparent border-0 cursor-pointer"
        >
          Mark all read
        </button>
      </div>
      {err && <p className="text-red-600 text-sm mb-4">{err}</p>}
      <ul className="space-y-3">
        {items.map((n) => (
          <li
            key={n.id}
            className={`rounded-lg border px-4 py-3 text-sm ${
              n.read_at ? "border-ink-muted/10 bg-paper" : "border-accent/30 bg-accent-light/30"
            }`}
          >
            <p className="text-ink">{n.body}</p>
            <p className="text-ink-faint text-xs mt-2">{n.created_at?.replace("T", " ").slice(0, 16)}</p>
            {!n.read_at && (
              <button
                type="button"
                className="mt-2 text-xs font-medium text-accent bg-transparent border-0 cursor-pointer p-0"
                onClick={() => markOne(n.id)}
              >
                Mark read
              </button>
            )}
          </li>
        ))}
      </ul>
      {items.length === 0 && !err && <p className="text-ink-muted text-sm">You’re all caught up.</p>}
    </div>
  );
}
