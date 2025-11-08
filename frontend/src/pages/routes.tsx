import RootPage from "./(main)/rootPage";
import ErrorPage from "./(main)/errorPage";
import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { lazy } from "react";
import AuthPage from "./(auth)/authPage";
import { ERouteNames } from "@/shared/lib/routeVariables";

const DashboardPage = lazy(() => import("@/pages/(main)/dashboardPage"));
const ProfilePage = lazy(() => import("@/pages/(main)/profilePage"));
const LandingPage = lazy(() => import("@/pages/(main)/landingPage"));
const RegisterPage = lazy(() => import("@/pages/(auth)/registerPage"));
const LoginPage = lazy(() => import("@/pages/(auth)/loginPage"));

export const routes = createBrowserRouter([
  {
    path: ERouteNames.DEFAULT_ROUTE,
    element: <RootPage />,
    errorElement: <ErrorPage />,
    children: [
      {
        path: ERouteNames.EMPTY_ROUTE,
        element: <Outlet />,
        children: [
          {
            path: ERouteNames.EMPTY_ROUTE,
            element: <Navigate to={ERouteNames.DASHBOARD_ROUTE} replace />,
          },
          {
            path: ERouteNames.DASHBOARD_ROUTE,
            element: <Outlet />,
            children: [
              {
                path: ERouteNames.EMPTY_ROUTE,
                element: <DashboardPage />,
              },
              {
                path: ERouteNames.PROFILE_ROUTE,
                element: <ProfilePage />,
              },
            ],
          },

          {
            path: ERouteNames.LANDING_ROUTE,
            element: <LandingPage />,
          },
        ],
      },
      {
        path: ERouteNames.AUTH_ROUTE,
        element: <AuthPage />,
        errorElement: <ErrorPage />,
        children: [
          {
            path: ERouteNames.EMPTY_ROUTE,
            element: <Navigate to={ERouteNames.REGISTER_ROUTE} replace />,
          },
          {
            path: ERouteNames.REGISTER_ROUTE,
            element: <RegisterPage />,
          },
          {
            path: ERouteNames.LOGIN_ROUTE,
            element: <LoginPage />,
          },
        ],
      },
    ],
  },
]);
