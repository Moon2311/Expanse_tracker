import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { useEffect, useState } from "react";
import api from "../api/apiClient.js";
import { unwrap } from "../utils/unwrap.js";

const linkClass = ({ isActive }) =>
  `block py-1.5 text-sm font-medium rounded-md px-2 -mx-2 ${
    isActive ? "text-accent bg-accent-light/50" : "text-ink-muted hover:text-ink"
  }`;

export default function Layout() {
  const { user, logout } = useAuth();
  const [unread, setUnread] = useState(0);
  const initial = (user?.username?.[0] || "?").toUpperCase();

  useEffect(() => {
    let cancel = false;
    const load = () => {
      api
        .get("/notifications/unread-count/")
        .then((res) => {
          if (!cancel) {
            const u = unwrap(res.data);
            setUnread(typeof u?.count === "number" ? u.count : 0);
          }
        })
        .catch(() => {});
    };
    load();
    const id = setInterval(load, 20000);
    return () => {
      cancel = true;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 shrink-0 border-r border-ink-muted/20 bg-paper-warm px-4 py-6 flex flex-col gap-6">
        <div>
          <NavLink to="/" className="flex items-center gap-2 font-semibold text-ink no-underline">
            <span className="text-accent text-xl" aria-hidden>
              ◈
            </span>
            <span>Spendly</span>
          </NavLink>
        </div>
        <nav className="flex flex-col gap-0.5" aria-label="Main">
          <NavLink to="/groups" className={linkClass}>
            Groups
          </NavLink>
          <NavLink to="/invites" className={linkClass}>
            Invites
          </NavLink>
          <NavLink to="/notifications" className={linkClass}>
            Notifications
            {unread > 0 && (
              <span className="ml-1 inline-flex min-w-[1.1rem] justify-center rounded-full bg-accent2 text-paper text-[0.65rem] px-1">
                {unread}
              </span>
            )}
          </NavLink>
          <NavLink to="/expenses" className={linkClass}>
            Expenses
          </NavLink>
          <NavLink to="/expenses/add" className={linkClass}>
            Add expense
          </NavLink>
          <NavLink to="/profile" className={linkClass}>
            Profile
          </NavLink>
          <button
            type="button"
            onClick={logout}
            className="text-left py-1.5 text-sm font-medium text-ink-faint hover:text-ink rounded-md px-2 -mx-2"
          >
            Sign out
          </button>
        </nav>
        <div className="mt-auto pt-4 border-t border-ink-muted/15">
          <div className="flex items-center gap-2">
            <span
              className="flex h-9 w-9 items-center justify-center rounded-full text-paper text-sm font-bold bg-gradient-to-br from-accent to-accent2"
              aria-hidden
            >
              {initial}
            </span>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-ink truncate">@{user?.username}</p>
              <p className="text-[0.7rem] text-ink-faint truncate">{user?.display_name || user?.email}</p>
            </div>
          </div>
        </div>
      </aside>
      <main className="flex-1 min-w-0 p-6 md:p-10 bg-paper">
        <Outlet />
      </main>
    </div>
  );
}
