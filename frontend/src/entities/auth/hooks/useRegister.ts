import { useMutation } from "@tanstack/react-query";
import { userRegister } from "../api/authService";
import { AuthResponse } from "../types/types";
import { setAccessToken } from "@/entities/token";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { useNavigate } from "react-router-dom";

export const REGISTER_QUERY = "register-query";

export const useRegisterMutation = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationKey: [REGISTER_QUERY],
    mutationFn: userRegister,
    onSuccess: (data: AuthResponse) => {
      setAccessToken(data.jwt);
      return navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    },
  });
};
