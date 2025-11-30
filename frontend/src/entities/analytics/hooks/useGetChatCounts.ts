import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../api/analyticsService";
import { ChatCountsResponse } from "../types/types";
import { GET_CHAT_COUNTS_QUERY } from "../lib/constants";

export const useGetChatCountsQuery = () => {
  return useQuery({
    queryKey: [GET_CHAT_COUNTS_QUERY],
    queryFn: async (): Promise<ChatCountsResponse> => {
      const response = await analyticsService.getChatCounts();
      return response;
    },
  });
};

