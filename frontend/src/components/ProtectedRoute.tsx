import { Navigate, useLocation } from "react-router-dom";
import type { PropsWithChildren } from "react";
import { useAuth } from "../features/auth/AuthContext";
import type { RoleKey } from "../types/user";

type Props = PropsWithChildren<{
  allowedRoles?: RoleKey[];
}>;

export default function ProtectedRoute({ allowedRoles, children }: Props) {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace state={{ from: location.pathname }} />;
  }

  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
