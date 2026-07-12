import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/app/layouts/AppLayout";
import { AuthLayout } from "@/app/layouts/AuthLayout";
import { PermissionRoute, ProtectedRoute, PublicRoute } from "@/app/guards";
import { ROUTES } from "@/shared/constants/app";
import { LoadingSkeleton } from "@/shared/components/feedback/states";

const LoginPage = lazy(() =>
  import("@/modules/auth/pages/LoginPage").then((module) => ({ default: module.LoginPage })),
);

const DashboardPage = lazy(() =>
  import("@/modules/dashboard/pages/DashboardPage").then((module) => ({
    default: module.DashboardPage,
  })),
);

const SocialPage = lazy(() =>
  import("@/modules/social/pages/SocialPage").then((module) => ({
    default: module.SocialPage,
  })),
);

const GovernancePage = lazy(() =>
  import("@/modules/governance/pages/GovernancePage").then((module) => ({
    default: module.GovernancePage,
  })),
);

const GamificationPage = lazy(() =>
  import("@/modules/gamification/pages/GamificationPage").then((module) => ({
    default: module.GamificationPage,
  })),
);

const EnvironmentalPage = lazy(() =>
  import("@/modules/environmental/pages/EnvironmentalPage").then((module) => ({
    default: module.EnvironmentalPage,
  })),
);

function RouteFallback() {
  return (
    <div className="flex min-h-[40vh] items-center justify-center">
      <LoadingSkeleton className="h-10 w-64" />
    </div>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<RouteFallback />}>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route element={<AuthLayout />}>
              <Route path={ROUTES.login} element={<LoginPage />} />
            </Route>
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route element={<PermissionRoute permission="dashboard:read" />}>
                <Route path={ROUTES.home} element={<DashboardPage />} />
              </Route>
              <Route element={<PermissionRoute permission="carbon:read" />}>
                <Route path={ROUTES.environmental} element={<EnvironmentalPage />} />
              </Route>
              <Route element={<PermissionRoute permission="csr:read" />}>
                <Route path={ROUTES.social} element={<SocialPage />} />
              </Route>
              <Route element={<PermissionRoute permission="policies:read" />}>
                <Route path={ROUTES.governance} element={<GovernancePage />} />
              </Route>
              <Route element={<PermissionRoute permission="challenges:read" />}>
                <Route path={ROUTES.gamification} element={<GamificationPage />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<Navigate to={ROUTES.home} replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
