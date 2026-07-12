import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/modules/auth/hooks/useAuth";
import { ROUTES } from "@/shared/constants/app";
import { ErrorState, LoadingSkeleton } from "@/shared/components/feedback/states";

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <LoadingSkeleton className="h-12 w-48" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.login} replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export function PublicRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  const redirectPath =
    (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? ROUTES.home;

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <LoadingSkeleton className="h-12 w-48" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to={redirectPath} replace />;
  }

  return <Outlet />;
}

interface PermissionRouteProps {
  permission: string;
  redirectTo?: string;
}

export function PermissionRoute({ permission, redirectTo = ROUTES.home }: PermissionRouteProps) {
  const { isAuthenticated, isLoading, hasPermission } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center p-6">
        <LoadingSkeleton className="h-10 w-48" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.login} replace />;
  }

  if (!hasPermission(permission)) {
    return (
      <div className="p-6">
        <ErrorState
          title="Access denied"
          message="You do not have permission to view this page."
        />
        <div className="mt-4">
          <a href={redirectTo} className="text-sm font-medium text-primary hover:underline">
            Return to home
          </a>
        </div>
      </div>
    );
  }

  return <Outlet />;
}
