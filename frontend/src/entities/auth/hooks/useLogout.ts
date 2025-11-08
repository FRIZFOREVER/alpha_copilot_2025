import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { logout } from "../api/authService";
import { ERouteNames } from "@/shared";
import { deleteAccessToken } from "@/entities/token";
import { queryClient } from "@/shared/api/queryClient";

export const LOGOUT_QUERY = "logout-query";

export const useLogoutMutation = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationKey: [LOGOUT_QUERY],
    mutationFn: logout,
    onSuccess: () => {
      // Удаляем токен из localStorage
      deleteAccessToken();
      
      // Очищаем кэш React Query
      queryClient.clear();
      
      // Перенаправляем на главную страницу
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    },
    onError: () => {
      // Даже если запрос на сервер не удался, выполняем локальный логаут
      deleteAccessToken();
      queryClient.clear();
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    },
  });
};
