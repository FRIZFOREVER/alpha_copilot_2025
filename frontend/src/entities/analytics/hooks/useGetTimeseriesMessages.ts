import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../api/analyticsService";
import {
  TimeseriesMessagesRequest,
  TimeseriesMessagesResponse,
} from "../types/types";
import { GET_TIMESERIES_MESSAGES_QUERY } from "../lib/constants";

export const useGetTimeseriesMessagesQuery = (
  request: TimeseriesMessagesRequest,
  enabled = true
) => {
  return useQuery({
    queryKey: [GET_TIMESERIES_MESSAGES_QUERY, request],
    queryFn: async (): Promise<TimeseriesMessagesResponse> => {
      const response = await analyticsService.getTimeseriesMessages(request);
      return response;
    },
    enabled,
  });
};

