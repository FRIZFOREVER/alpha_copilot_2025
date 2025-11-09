import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { TypeLoginSchema } from "../lib/schemes/loginSchema";
import { userLogin } from "../api/authService";
import { setAccessToken } from "@/entities/token";
import { AuthResponse } from "../types/types";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const LOGIN_QUERY = "login-query";

export const useLoginMutation = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationKey: [LOGIN_QUERY],
    mutationFn: (data: TypeLoginSchema) => userLogin(data),
    onSuccess: (data: AuthResponse) => {
      setAccessToken(data.jwt);
      return navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    },
  });
};
