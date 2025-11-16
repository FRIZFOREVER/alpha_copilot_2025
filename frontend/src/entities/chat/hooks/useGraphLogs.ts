import { useQuery } from "@tanstack/react-query";
import { getGraphLogs } from "../api/chatService";
import { GetGraphLogsResponse } from "../types/types";

export const GET_GRAPH_LOGS_QUERY = "get-graph-logs-query";

export const useGraphLogsQuery = (answerId: number | undefined) => {
  return useQuery({
    queryKey: [GET_GRAPH_LOGS_QUERY, answerId],
    queryFn: async (): Promise<GetGraphLogsResponse> => {
      if (!answerId) {
        throw new Error("Answer ID is required");
      }
      const response = await getGraphLogs(answerId);
      return response;
    },
    retry: false,
    enabled: !!answerId,
  });
};
