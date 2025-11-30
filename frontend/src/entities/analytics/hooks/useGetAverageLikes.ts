import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../api/analyticsService";
import { AverageLikesResponse } from "../types/types";
import { GET_AVERAGE_LIKES_QUERY } from "../lib/constants";

export const useGetAverageLikesQuery = () => {
  return useQuery({
    queryKey: [GET_AVERAGE_LIKES_QUERY],
    queryFn: async (): Promise<AverageLikesResponse> => {
      const response = await analyticsService.getAverageLikes();
      return response;
    },
  });
};

