import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../api/analyticsService";
import { FileCountsResponse } from "../types/types";
import { GET_FILE_COUNTS_QUERY } from "../lib/constants";

export const useGetFileCountsQuery = () => {
  return useQuery({
    queryKey: [GET_FILE_COUNTS_QUERY],
    queryFn: async (): Promise<FileCountsResponse> => {
      const response = await analyticsService.getFileCounts();
      return response;
    },
  });
};

