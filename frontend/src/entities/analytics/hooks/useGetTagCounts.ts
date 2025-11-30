import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../api/analyticsService";
import { TagCountsResponse } from "../types/types";
import { GET_TAG_COUNTS_QUERY } from "../lib/constants";

export const useGetTagCountsQuery = () => {
  return useQuery({
    queryKey: [GET_TAG_COUNTS_QUERY],
    queryFn: async (): Promise<TagCountsResponse> => {
      const response = await analyticsService.getTagCounts();
      return response;
    },
  });
};
