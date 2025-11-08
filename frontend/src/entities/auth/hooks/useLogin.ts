import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { TypeLoginSchema } from "../lib/schemes/loginSchema";
import { userLogin } from "../api/authService";
import { ERouteNames } from "@/shared";
import { setAccessToken } from "@/entities/token";
import { EProfileRoles, Profile } from "@/entities/profile/types/types";

export const LOGIN_QUERY = "login-query";

export const useLoginMutation = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationKey: [LOGIN_QUERY],
    mutationFn: (data: TypeLoginSchema) => userLogin(data),
    onSuccess: (data: Profile) => {
      setAccessToken(crypto.randomUUID());
      if (data.role === EProfileRoles.COMPANY) {
        return navigate(`/${ERouteNames.DASHBOARD_COMPANY_ROUTE}`);
      }

      if (data.role === EProfileRoles.UNIVERSITY) {
        return navigate(`/${ERouteNames.DASHBOARD_UNIVERSITY_ROUTE}`);
      }

      if (data.role === EProfileRoles.ADMIN) {
        return navigate(`/${ERouteNames.DASHBOARD_ADMIN_ROUTE}`);
      }
    },
  });
};
