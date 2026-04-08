import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../api/apiClient.js";
import { getErrorMessage } from "../utils/errors.js";

export default function GroupExpenseNew() {
  const { groupId } = useParams();
  const nav = useNavigate();
  const [amount, setAmount] = useState("");
  const [spentOn, setSpentOn] = useState(() => new Date().toISOString().slice(0, 10));
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");
    try {
      await api.post(`/groups/${groupId}/expenses/`, {
        amount,
        spent_on: spentOn,
        description,
        category,
      });
      nav(`/groups/${groupId}`);
    } catch (ex) {
      setErr(getErrorMessage(ex));
    }
  }

  return (
    <div className="max-w-md">
      <p className="text-sm mb-4">
        <Link to={`/groups/${groupId}`} className="text-accent no-underline">
          ← Back to group
        </Link>
      </p>
      <h1 className="font-display text-2xl text-ink mb-6">Add group expense</h1>
      {err && <p className="text-red-600 text-sm mb-4">{err}</p>}
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-xs text-ink-muted mb-1">Amount</label>
          <input
            required
            className="w-full rounded-md border border-ink-muted/25 px-3 py-2 text-sm"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-ink-muted mb-1">Date</label>
          <input
            type="date"
            required
            className="w-full rounded-md border border-ink-muted/25 px-3 py-2 text-sm"
            value={spentOn}
            onChange={(e) => setSpentOn(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-ink-muted mb-1">Category</label>
          <input
            className="w-full rounded-md border border-ink-muted/25 px-3 py-2 text-sm"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-ink-muted mb-1">Note</label>
          <input
            className="w-full rounded-md border border-ink-muted/25 px-3 py-2 text-sm"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <button type="submit" className="rounded-md bg-accent text-paper px-5 py-2 text-sm font-semibold">
          Save
        </button>
      </form>
    </div>
  );
}
