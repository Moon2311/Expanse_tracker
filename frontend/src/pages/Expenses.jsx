import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/apiClient.js";
import { getErrorMessage } from "../utils/errors.js";

export default function Expenses() {
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .get("/expenses/")
      .then((r) => setRows(Array.isArray(r.data) ? r.data : []))
      .catch((e) => setErr(getErrorMessage(e)));
  }, []);

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <h1 className="font-display text-3xl text-ink">Expenses</h1>
        <Link
          to="/expenses/add"
          className="rounded-md bg-accent text-paper px-4 py-2 text-sm font-semibold no-underline"
        >
          Add expense
        </Link>
      </div>
      {err && <p className="text-red-600 text-sm mb-4">{err}</p>}
      <ul className="space-y-2">
        {rows.map((ex) => (
          <li key={ex.id} className="rounded-lg border border-ink-muted/15 bg-paper-warm px-4 py-3 text-sm">
            <span className="font-semibold">₹{Number(ex.amount).toFixed(2)}</span>
            <span className="text-ink-muted ml-2">{ex.spent_on}</span>
            <p className="text-ink-muted">{ex.description || ex.category || "—"}</p>
          </li>
        ))}
      </ul>
      {rows.length === 0 && !err && <p className="text-ink-muted text-sm">No personal expenses yet.</p>}
    </div>
  );
}
