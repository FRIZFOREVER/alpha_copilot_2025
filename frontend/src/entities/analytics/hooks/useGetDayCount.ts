import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../api/analyticsService";
import { DayCountResponse } from "../types/types";
import { GET_DAY_COUNT_QUERY } from "../lib/constants";

export const useGetDayCountQuery = () => {
  return useQuery({
    queryKey: [GET_DAY_COUNT_QUERY],
    queryFn: async (): Promise<DayCountResponse> => {
      const response = await analyticsService.getDayCount();
      return response;
    },
  });
};

