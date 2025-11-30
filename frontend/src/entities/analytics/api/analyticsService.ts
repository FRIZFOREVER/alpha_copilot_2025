import { axiosAuth } from "@/shared/api/baseQueryInstance";
import {
  AverageLikesResponse,
  ChatCountsResponse,
  DayCountResponse,
  FileCountsResponse,
  TagCountsResponse,
  TimeseriesMessagesRequest,
  TimeseriesMessagesResponse,
} from "../types/types";

class AnalyticsService {
  public async getAverageLikes(): Promise<AverageLikesResponse> {
    const { data } = await axiosAuth.get<AverageLikesResponse>(
      "/analytics/average-likes"
    );
    return data;
  }

  public async getChatCounts(): Promise<ChatCountsResponse> {
    const { data } = await axiosAuth.get<ChatCountsResponse>(
      "/analytics/chat-counts"
    );
    return data;
  }

  public async getDayCount(): Promise<DayCountResponse> {
    const { data } = await axiosAuth.get<DayCountResponse>(
      "/analytics/day-count"
    );
    return data;
  }

  public async getFileCounts(): Promise<FileCountsResponse> {
    const { data } = await axiosAuth.get<FileCountsResponse>(
      "/analytics/file-counts"
    );
    return data;
  }

  public async getTagCounts(): Promise<TagCountsResponse> {
    const { data } = await axiosAuth.get<TagCountsResponse>(
      "/analytics/tag-counts"
    );
    return data;
  }

  public async getTimeseriesMessages(
    request: TimeseriesMessagesRequest
  ): Promise<TimeseriesMessagesResponse> {
    const { data } = await axiosAuth.post<TimeseriesMessagesResponse>(
      "/analytics/timeseries-messages",
      request
    );
    return data;
  }
}

export const analyticsService = new AnalyticsService();

