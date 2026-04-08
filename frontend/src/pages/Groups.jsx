import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/apiClient.js";
import { getErrorMessage } from "../utils/errors.js";

export default function Groups() {
  const [groups, setGroups] = useState([]);
  const [q, setQ] = useState("");
  const [name, setName] = useState("");
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    try {
      const { data } = await api.get("/search/groups/", { params: { q } });
      setGroups(data);
    } catch (e) {
      setErr(getErrorMessage(e));
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function createGroup(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setErr("");
    try {
      await api.post("/groups/", { name: name.trim() });
      setName("");
      load();
    } catch (e) {
      setErr(getErrorMessage(e));
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl text-ink mb-2">Groups</h1>
      <p className="text-ink-muted text-sm mb-6">Search groups you belong to, or create a new one.</p>
      {err && <p className="text-red-600 text-sm mb-4">{err}</p>}
      <form onSubmit={(e) => e.preventDefault() || load()} className="flex flex-wrap gap-2 mb-8">
        <input
          placeholder="Search by name…"
          className="flex-1 min-w-[12rem] rounded-md border border-ink-muted/25 px-3 py-2 text-sm"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button type="submit" className="rounded-md bg-ink/90 text-paper px-4 py-2 text-sm font-medium">
          Search
        </button>
      </form>
      <form onSubmit={createGroup} className="flex flex-wrap gap-2 mb-10 items-end">
        <div>
          <label className="block text-xs text-ink-muted mb-1">New group</label>
          <input
            placeholder="Group name"
            className="rounded-md border border-ink-muted/25 px-3 py-2 text-sm w-56"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <button type="submit" className="rounded-md bg-accent text-paper px-4 py-2 text-sm font-semibold">
          Create
        </button>
      </form>
      <ul className="space-y-2">
        {groups.map((g) => (
          <li key={g.id}>
            <Link to={`/groups/${g.id}`} className="block rounded-lg border border-ink-muted/15 bg-paper-warm px-4 py-3 hover:border-accent/40 no-underline text-ink">
              <span className="font-semibold">{g.name}</span>
              <span className="text-ink-muted text-sm ml-2">{g.member_count} members</span>
            </Link>
          </li>
        ))}
      </ul>
      {groups.length === 0 && <p className="text-ink-muted text-sm">No groups yet.</p>}
    </div>
  );
}
