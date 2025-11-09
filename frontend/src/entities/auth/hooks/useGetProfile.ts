import { useQuery } from "@tanstack/react-query";
import { getProfile } from "../api/authService";
import { ProfileResponse } from "../types/types";

export const GET_PROFILE_QUERY = "get-profile-query";

export const useGetProfileQuery = () => {
  return useQuery({
    queryKey: [GET_PROFILE_QUERY],
    queryFn: async (): Promise<ProfileResponse> => {
      const response = await getProfile();
      return response;
    },
  });
};

