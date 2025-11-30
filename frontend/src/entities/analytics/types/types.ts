export interface NullableFloat {
  Float64: number;
  Valid: boolean;
}

export interface AverageLikesResponse {
  avg_rating: NullableFloat;
  avg_rating_yesterday: NullableFloat;
}

export interface ChatCountsResponse {
  count_chats: number;
  count_chats_yesterday: number;
}

export interface DayCountResponse {
  count_days: number;
}

export interface FileCountsResponse {
  count_messages: number;
  count_messages_yesterday: number;
}

export interface TagCount {
  tag: string;
  tag_count: number;
}

export type TagCountsResponse = TagCount[];

export interface TimeseriesMessagesRequest {
  start_date: string;
  end_date: string;
}

export interface TimeseriesMessage {
  day: string;
  count_messages: number;
}

export type TimeseriesMessagesResponse = TimeseriesMessage[];
