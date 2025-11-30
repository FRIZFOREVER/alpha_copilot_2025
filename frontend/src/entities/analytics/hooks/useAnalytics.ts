import { useGetAverageLikesQuery } from "./useGetAverageLikes";
import { useGetChatCountsQuery } from "./useGetChatCounts";
import { useGetDayCountQuery } from "./useGetDayCount";
import { useGetFileCountsQuery } from "./useGetFileCounts";
import { useGetTagCountsQuery } from "./useGetTagCounts";
import { TimeseriesMessagesRequest } from "../types/types";
import { useGetTimeseriesMessagesQuery } from "./useGetTimeseriesMessages";

export interface UseAnalyticsOptions {
  timeseriesRequest?: TimeseriesMessagesRequest;
  enableTimeseries?: boolean;
}

export const useAnalytics = (options?: UseAnalyticsOptions) => {
  const averageLikes = useGetAverageLikesQuery();
  const chatCounts = useGetChatCountsQuery();
  const dayCount = useGetDayCountQuery();
  const fileCounts = useGetFileCountsQuery();
  const tagCounts = useGetTagCountsQuery();
  const timeseriesMessages = useGetTimeseriesMessagesQuery(
    options?.timeseriesRequest || {
      start_date: "",
      end_date: "",
    },
    options?.enableTimeseries ?? false
  );

  return {
    averageLikes,
    chatCounts,
    dayCount,
    fileCounts,
    tagCounts,
    timeseriesMessages,
    isLoading:
      averageLikes.isLoading ||
      chatCounts.isLoading ||
      dayCount.isLoading ||
      fileCounts.isLoading ||
      tagCounts.isLoading ||
      (options?.enableTimeseries && timeseriesMessages.isLoading),
    isError:
      averageLikes.isError ||
      chatCounts.isError ||
      dayCount.isError ||
      fileCounts.isError ||
      tagCounts.isError ||
      (options?.enableTimeseries && timeseriesMessages.isError),
  };
};
