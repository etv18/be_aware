import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { useSession } from '@/lib/queries';

/** Pages inside it need a logged in user; anyone else goes to the login form and comes back after. */
export function RequireAuth() {
  const session = useSession();
  const location = useLocation();

  if (session.isPending) return null;
  if (!session.data?.data.authenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <Outlet />;
}
