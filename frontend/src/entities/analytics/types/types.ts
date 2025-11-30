// Типы для average-likes
export interface NullableFloat {
  Float64: number;
  Valid: boolean;
}

export interface AverageLikesResponse {
  avg_rating: NullableFloat;
  avg_rating_yesterday: NullableFloat;
}

// Типы для chat-counts
export interface ChatCountsResponse {
  count_chats: number;
  count_chats_yesterday: number;
}

// Типы для day-count
export interface DayCountResponse {
  count_days: number;
}

// Типы для file-counts
export interface FileCountsResponse {
  count_messages: number;
  count_messages_yesterday: number;
}

// Типы для tag-counts
export interface TagCount {
  tag: string;
  tag_count: number;
}

export type TagCountsResponse = TagCount[];

// Типы для timeseries-messages
export interface TimeseriesMessagesRequest {
  start_date: string;
  end_date: string;
}

export interface TimeseriesMessage {
  day: string;
  count_messages: number;
}

export type TimeseriesMessagesResponse = TimeseriesMessage[];

