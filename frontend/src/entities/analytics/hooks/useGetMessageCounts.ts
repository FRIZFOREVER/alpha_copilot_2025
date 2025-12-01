import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../api/analyticsService";
import { MessageCountsResponse } from "../types/types";
import { GET_MESSAGE_COUNTS_QUERY } from "../lib/constants";

export const useGetMessageCountsQuery = () => {
  return useQuery({
    queryKey: [GET_MESSAGE_COUNTS_QUERY],
    queryFn: async (): Promise<MessageCountsResponse> => {
      const response = await analyticsService.getMessageCounts();
      return response;
    },
  });
};

