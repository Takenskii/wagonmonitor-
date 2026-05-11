/** Wrap a route to redirect to /login if there's no current user. */
import { Navigate, useLocation } from 'react-router-dom';
import type { ReactElement } from 'react';

import { useAuth } from '../auth/useAuth';

export function RequireAuth({ children }: { children: ReactElement }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}
