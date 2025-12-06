export interface BaseMessage {
  id: string;
  content: string;
  timestamp?: string;
  tag: string;
}

export interface UserMessage extends BaseMessage {
  isUser: true;
  file_url?: string;
}

export interface BotMessage extends BaseMessage {
  isUser: false;
  answerId?: number;
  rating?: number | null;
  isTyping?: boolean;
  answer_file_url?: string;
  voice_url?: string;
}

export type MessageData = UserMessage | BotMessage;

