import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { logout } from "../api/authService";
import { deleteAccessToken } from "@/entities/token";
import { queryClient } from "@/shared/api/queryClient";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const LOGOUT_QUERY = "logout-query";

export const useLogoutMutation = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationKey: [LOGOUT_QUERY],
    mutationFn: logout,
    onSuccess: () => {
      deleteAccessToken();

      queryClient.clear();

      navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    },
    onError: () => {
      deleteAccessToken();
      queryClient.clear();
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    },
  });
};
