import { Navigate, Outlet } from 'react-router-dom';

import type { Role } from '../api/types';
import { useAuthStore } from '../store/authStore';

interface RoleRouteProps {
  allowed: Role[];
}

export function RoleRoute({ allowed }: RoleRouteProps) {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowed.includes(user.role)) {
    return <Navigate to="/app/dashboard" replace />;
  }

  return <Outlet />;
}
