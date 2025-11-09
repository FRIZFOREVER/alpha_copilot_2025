import RootPage from "./(main)/rootPage";
import ErrorPage from "./(main)/errorPage";
import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { lazy } from "react";
import AuthPage from "./(auth)/authPage";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { privatePage } from "@/entities/viewer/lib/hoc/privatePage";
import { routesWithHoc } from "@/shared/lib/routesWithHoc";
import { chatDetailAction } from "@/entities/chat/action/chatRedirectAction";

const DashboardPage = lazy(() => import("@/pages/(main)/dashboardPage"));
const ProfilePage = lazy(() => import("@/pages/(main)/profilePage"));
const CopilotChatPage = lazy(() => import("@/pages/(main)/copilotChatPage"));

const LandingPage = lazy(() => import("@/pages/(main)/landingPage"));
const RegisterPage = lazy(() => import("@/pages/(auth)/registerPage"));
const LoginPage = lazy(() => import("@/pages/(auth)/loginPage"));

export const routes = createBrowserRouter([
  {
    path: ERouteNames.DEFAULT_ROUTE,
    element: <RootPage />,
    errorElement: <ErrorPage />,
    children: [
      ...routesWithHoc(privatePage, [
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
                  children: [
                    {
                      path: ERouteNames.EMPTY_ROUTE,
                      element: <Navigate to={ERouteNames.CHAT_ROUTE} replace />,
                    },
                    {
                      path: ERouteNames.CHAT_ROUTE,
                      loader: chatDetailAction,
                    },
                    {
                      path: ERouteNames.CHAT_DETAIL_ROUTE,
                      element: <CopilotChatPage />,
                    },
                  ],
                },
                {
                  path: ERouteNames.PROFILE_ROUTE,
                  element: <ProfilePage />,
                },
              ],
            },
          ],
        },
      ]),
      {
        path: ERouteNames.LANDING_ROUTE,
        element: <LandingPage />,
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
