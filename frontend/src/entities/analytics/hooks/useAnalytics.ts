import { useGetAverageLikesQuery } from "./useGetAverageLikes";
import { useGetChatCountsQuery } from "./useGetChatCounts";
import { useGetDayCountQuery } from "./useGetDayCount";
import { useGetFileCountsQuery } from "./useGetFileCounts";
import { useGetMessageCountsQuery } from "./useGetMessageCounts";
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
  const messageCounts = useGetMessageCountsQuery();
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
    messageCounts,
    tagCounts,
    timeseriesMessages,
    isLoading:
      averageLikes.isLoading ||
      chatCounts.isLoading ||
      dayCount.isLoading ||
      fileCounts.isLoading ||
      messageCounts.isLoading ||
      tagCounts.isLoading ||
      (options?.enableTimeseries && timeseriesMessages.isLoading),
    isError:
      averageLikes.isError ||
      chatCounts.isError ||
      dayCount.isError ||
      fileCounts.isError ||
      messageCounts.isError ||
      tagCounts.isError ||
      (options?.enableTimeseries && timeseriesMessages.isError),
  };
};
