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

// История чата
export interface HistoryMessage {
  question_id: number;
  answer_id: number;
  question: string;
  answer: string;
  question_time: string;
  answer_time: string;
  voice_url: string;
  rating: number | null;
}

export type GetHistoryResponse = HistoryMessage[];

// Лайк на сообщение
export interface LikeMessageDto {
  answer_id: number;
  rating: number;
}

export interface LikeMessageResponse {
  answer_id: number;
  like: boolean;
}

// Отправка сообщения
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

// Отправка голосового сообщения
export interface SendVoiceResponse {
  question: string;
  voice_url: string;
}

