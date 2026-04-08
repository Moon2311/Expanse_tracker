import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import { useAuth } from "./context/AuthContext.jsx";
import AddExpense from "./pages/AddExpense.jsx";
import Expenses from "./pages/Expenses.jsx";
import GroupDetail from "./pages/GroupDetail.jsx";
import GroupExpenseNew from "./pages/GroupExpenseNew.jsx";
import Groups from "./pages/Groups.jsx";
import Home from "./pages/Home.jsx";
import Invites from "./pages/Invites.jsx";
import Login from "./pages/Login.jsx";
import Notifications from "./pages/Notifications.jsx";
import Profile from "./pages/Profile.jsx";
import Register from "./pages/Register.jsx";

function Protected({ children }) {
  const { ready, isAuthenticated } = useAuth();
  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center text-ink-muted text-sm">
        Loading…
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route path="/" element={<Home />} />
        <Route path="/groups" element={<Groups />} />
        <Route path="/groups/:groupId" element={<GroupDetail />} />
        <Route path="/groups/:groupId/expense/new" element={<GroupExpenseNew />} />
        <Route path="/invites" element={<Invites />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/expenses" element={<Expenses />} />
        <Route path="/expenses/add" element={<AddExpense />} />
        <Route path="/profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
