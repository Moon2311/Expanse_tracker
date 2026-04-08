import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api/apiClient.js";
import { usePolling } from "../hooks/usePolling.js";
import { getErrorMessage } from "../utils/errors.js";
import { unwrap } from "../utils/unwrap.js";

export default function GroupDetail() {
  const { groupId } = useParams();
  const [group, setGroup] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [messages, setMessages] = useState([]);
  const [inviteUser, setInviteUser] = useState("");
  const [chatBody, setChatBody] = useState("");
  const [userQ, setUserQ] = useState("");
  const [searchHits, setSearchHits] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .get(`/groups/${groupId}/`)
      .then((r) => setGroup(r.data))
      .catch((e) => setErr(getErrorMessage(e)));
  }, [groupId]);

  function loadExpenses() {
    api
      .get(`/groups/${groupId}/expenses/`)
      .then((r) => setExpenses(Array.isArray(r.data) ? r.data : []))
      .catch(() => setExpenses([]));
  }

  function loadChat() {
    api
      .get(`/groups/${groupId}/chat/`)
      .then((r) => {
        const d = unwrap(r.data);
        setMessages(Array.isArray(d) ? d : []);
      })
      .catch(() => setMessages([]));
  }

  useEffect(() => {
    loadExpenses();
    loadChat();
  }, [groupId]);

  usePolling(loadChat, 4000, !!groupId);

  async function sendChat(e) {
    e.preventDefault();
    if (!chatBody.trim()) return;
    setErr("");
    try {
      await api.post(`/groups/${groupId}/chat/`, { body: chatBody.trim() });
      setChatBody("");
      loadChat();
    } catch (ex) {
      setErr(getErrorMessage(ex));
    }
  }

  async function invite(e) {
    e.preventDefault();
    if (!inviteUser.trim()) return;
    setErr("");
    try {
      await api.post(`/groups/${groupId}/invites/`, { username: inviteUser.trim() });
      setInviteUser("");
    } catch (ex) {
      setErr(getErrorMessage(ex));
    }
  }

  useEffect(() => {
    if (userQ.trim().length < 2) {
      setSearchHits([]);
      return;
    }
    const t = setTimeout(() => {
      api
        .get("/search/users/", { params: { q: userQ.trim() } })
        .then((r) => setSearchHits(Array.isArray(r.data) ? r.data : []))
        .catch(() => setSearchHits([]));
    }, 300);
    return () => clearTimeout(t);
  }, [userQ]);

  if (!group) {
    return err ? <p className="text-red-600">{err}</p> : <p className="text-ink-muted">Loading…</p>;
  }

  return (
    <div className="max-w-4xl">
      <p className="text-sm text-ink-muted mb-2">
        <Link to="/groups" className="text-accent no-underline">
          ← Groups
        </Link>
      </p>
      <h1 className="font-display text-3xl text-ink mb-1">{group.name}</h1>
      <p className="text-ink-muted text-sm mb-8">{group.member_count} members</p>
      {err && <p className="text-red-600 text-sm mb-4">{err}</p>}

      <div className="grid gap-8 lg:grid-cols-2">
        <section>
          <h2 className="text-lg font-semibold mb-3">Expenses</h2>
          <ul className="space-y-2 mb-6 text-sm">
            {expenses.map((ex) => (
              <li key={ex.id} className="rounded-lg border border-ink-muted/15 px-3 py-2 bg-paper-warm">
                <span className="font-semibold">₹{Number(ex.amount).toFixed(2)}</span>
                <span className="text-ink-muted ml-2">{ex.spent_on}</span>
                <p className="text-ink-muted">{ex.description || ex.category || "—"}</p>
              </li>
            ))}
          </ul>
          <Link
            to={`/groups/${groupId}/expense/new`}
            className="inline-block text-sm font-medium text-accent no-underline"
          >
            + Add group expense
          </Link>
        </section>

        <section className="flex flex-col min-h-[320px] border border-ink-muted/15 rounded-xl bg-paper-warm overflow-hidden">
          <h2 className="text-lg font-semibold px-4 pt-4 pb-2">Group chat</h2>
          <div className="flex-1 overflow-y-auto px-4 space-y-2 max-h-72 text-sm">
            {messages.map((m) => (
              <div key={m.id} className="rounded-lg bg-paper px-3 py-2 border border-ink-muted/10">
                <span className="text-accent font-semibold text-xs">@{m.sender_username}</span>
                <p className="text-ink mt-0.5 whitespace-pre-wrap">{m.body}</p>
                <p className="text-[0.65rem] text-ink-faint mt-1">{m.created_at?.replace("T", " ").slice(0, 16)}</p>
              </div>
            ))}
          </div>
          <form onSubmit={sendChat} className="p-3 border-t border-ink-muted/15 flex gap-2">
            <input
              className="flex-1 rounded-md border border-ink-muted/25 px-3 py-2 text-sm"
              placeholder="Message…"
              value={chatBody}
              onChange={(e) => setChatBody(e.target.value)}
            />
            <button type="submit" className="rounded-md bg-accent text-paper px-4 py-2 text-sm font-semibold">
              Send
            </button>
          </form>
        </section>
      </div>

      <section className="mt-10 border-t border-ink-muted/15 pt-8">
        <h2 className="text-lg font-semibold mb-3">Invite by username</h2>
        <form onSubmit={invite} className="flex flex-wrap gap-2 mb-6">
          <input
            className="rounded-md border border-ink-muted/25 px-3 py-2 text-sm w-48"
            placeholder="username"
            value={inviteUser}
            onChange={(e) => setInviteUser(e.target.value)}
          />
          <button type="submit" className="rounded-md bg-ink text-paper px-4 py-2 text-sm font-medium">
            Send invite
          </button>
        </form>
        <div>
          <label className="block text-xs text-ink-muted mb-1">Search users (min 2 chars)</label>
          <input
            className="rounded-md border border-ink-muted/25 px-3 py-2 text-sm w-full max-w-xs mb-2"
            value={userQ}
            onChange={(e) => setUserQ(e.target.value)}
          />
          <ul className="text-sm space-y-1">
            {searchHits.map((u) => (
              <li key={u.id}>
                <button
                  type="button"
                  className="text-accent hover:underline"
                  onClick={() => setInviteUser(u.username)}
                >
                  @{u.username}
                </button>{" "}
                <span className="text-ink-muted">{u.display_name}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}
