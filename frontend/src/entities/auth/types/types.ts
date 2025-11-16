import { ApiStatus, TelegramAuthStatus } from "@/shared/types/api";

export interface LoginDto {
  login: string;
  password: string;
}

export interface RegisterDto extends Pick<LoginDto, "login" | "password"> {
  username: string;
}

export interface AuthResponse {
  jwt: string;
}

export interface ProfileResponse {
  id: number;
  login: string;
  username: string;
  user_info: string;
  business_info: string;
  additional_instructions: string;
}

export interface UpdateProfileDto {
  user_info: string;
  business_info: string;
  additional_instructions: string;
}

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name: string | null;
  username: string | null;
  phone_number: string;
}

export interface TelegramAuthStartRequest {
  user_id: string;
  phone_number: string;
}

export interface TelegramAuthStartResponse {
  status: Extract<TelegramAuthStatus, "ok" | "error" | "code_sent">;
  phone_code_hash?: string;
  message?: string;
  error?: string;
}

export interface TelegramAuthVerifyRequest {
  user_id: string;
  phone_code: string;
  password?: string;
}

export interface TelegramAuthVerifyResponse {
  status: Extract<TelegramAuthStatus, "ok" | "error" | "password_required">;
  message?: string;
  error?: string;
  user?: TelegramUser;
}

export interface TelegramStatusRequest {
  phone_number: string;
}

export interface TelegramStatusResponse {
  status: "ok";
  authorized: boolean;
  user_info?: TelegramUser;
}

export interface TelegramContact extends TelegramUser {
  is_contact: boolean;
}

export interface TelegramContactsRequest {
  phone_number?: string;
  tg_user_id?: number;
}

export interface TelegramContactsResponse {
  status: ApiStatus;
  contacts: TelegramContact[];
  error?: string;
}

export interface TelegramSendMessageRequest {
  phone_number: string;
  recipient_id: number | string;
  text: string;
}

export interface TelegramSendMessageResponse {
  status: ApiStatus;
  success?: boolean;
  message_id?: number;
  date?: string;
  error?: string;
}

export interface TodoistAuthSaveRequest {
  user_id: string;
  token: string;
}

export interface TodoistAuthSaveResponse {
  status: ApiStatus;
  message?: string;
  error?: string;
}

export interface TodoistStatusRequest {
  user_id: string;
}

export interface TodoistStatusResponse {
  status: "ok";
  authorized: boolean;
}

export interface TodoistCreateTaskRequest {
  user_id: string;
  content: string;
  description?: string;
  labels?: string[];
}

export interface TodoistCreateTaskResponse {
  status: ApiStatus;
  task_id?: string;
  content?: string;
  url?: string;
  message?: string;
  error?: string;
}
