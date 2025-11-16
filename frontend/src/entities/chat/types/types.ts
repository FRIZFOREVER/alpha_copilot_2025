export interface CreateChatDto {
  name: string;
}

export interface CreateChatResponse {
  chat_id: number;
}

export interface Chat {
  chat_id: number;
  name: string;
  create_time: string;
}

export type GetChatsResponse = Chat[];

export interface HistoryMessage {
  question_id: number;
  answer_id: number;
  question: string;
  answer: string;
  question_time: string;
  answer_time: string;
  voice_url: string;
  file_url?: string;
  rating: number | null;
  tag: string;
}

export type GetHistoryResponse = HistoryMessage[];

export interface LikeMessageDto {
  answer_id: number;
  rating: number;
}

export interface LikeMessageResponse {
  answer_id: number;
  like: boolean;
}

export interface SendMessageDto {
  question: string;
}

export interface SendMessageResponse {
  question_id: number;
  answer_id: number;
  answer: string;
  question_time: string;
  answer_time: string;
  is_support_needed: boolean;
}

export interface SendVoiceResponse {
  question: string;
  voice_url: string;
}

export interface UploadFileResponse {
  file_url: string;
}

import { ModelMode } from "@/shared/types/modelMode";

export interface SendMessageStreamDto {
  question: string;
  voice_url?: string;
  file_url?: string;
  tag?: string;
  mode?: ModelMode;
  profile: {
    id: number;
    login: string;
    fio: string;
    user_info: string;
    business_info: string;
    additional_instructions: string;
  };
}

export interface StreamInitialResponse {
  question_id: number;
  answer_id: number;
  question_time: string;
  tag: string;
}

export interface StreamChunk {
  content: string;
  thinking: string;
  time: string;
  done: boolean;
  tag?: string;
}

export interface SendMessageStreamCallbacks {
  onInitial?: (data: StreamInitialResponse) => void;
  onChunk?: (chunk: StreamChunk) => void;
  onComplete?: () => void;
  onError?: (error: Error) => void;
}

export interface SearchMessageResult extends Omit<HistoryMessage, "tag"> {
  file_url: string;
}

export type SearchMessagesResponse = SearchMessageResult[] | null;

export interface GraphLog {
  id: number;
  tag: string;
  message: string;
  log_time: string;
  answer_id: number;
}

export type GetGraphLogsResponse = GraphLog[];

export interface GraphLogWebSocketMessage {
  tag: string;
  answer_id: number;
  message: string;
}
