import { useEffect, useState } from "react";
import api from "../api/apiClient.js";
import { getErrorMessage } from "../utils/errors.js";

export default function Invites() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  function load() {
    api
      .get("/invitations/pending/")
      .then((r) => setItems(Array.isArray(r.data) ? r.data : []))
      .catch((e) => setErr(getErrorMessage(e)));
  }

  useEffect(() => {
    load();
  }, []);

  async function accept(id) {
    try {
      await api.post(`/invitations/${id}/accept/`);
      load();
    } catch (e) {
      setErr(getErrorMessage(e));
    }
  }

  async function decline(id) {
    try {
      await api.post(`/invitations/${id}/decline/`);
      load();
    } catch (e) {
      setErr(getErrorMessage(e));
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl text-ink mb-8">Invites</h1>
      {err && <p className="text-red-600 text-sm mb-4">{err}</p>}
      <ul className="space-y-3">
        {items.map((inv) => (
          <li key={inv.id} className="rounded-lg border border-ink-muted/15 bg-paper-warm px-4 py-3 text-sm flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="font-medium">{inv.group_name}</p>
              <p className="text-ink-muted text-xs">From @{inv.inviter_username}</p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => accept(inv.id)}
                className="rounded-md bg-accent text-paper px-3 py-1.5 text-xs font-semibold"
              >
                Accept
              </button>
              <button
                type="button"
                onClick={() => decline(inv.id)}
                className="rounded-md border border-ink-muted/25 px-3 py-1.5 text-xs font-medium"
              >
                Decline
              </button>
            </div>
          </li>
        ))}
      </ul>
      {items.length === 0 && !err && <p className="text-ink-muted text-sm">No pending invitations.</p>}
    </div>
  );
}
