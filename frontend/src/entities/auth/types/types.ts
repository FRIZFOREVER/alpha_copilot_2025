export interface LoginDto {
  login: string;
  password: string;
}

export interface RegisterDto {
  login: string;
  username: string;
  password: string;
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

// Telegram Integration Types
export interface TelegramAuthStartRequest {
  user_id: string;
  phone_number: string;
}

export interface TelegramAuthStartResponse {
  status: "ok" | "error" | "code_sent";
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
  status: "ok" | "error" | "password_required";
  message?: string;
  error?: string;
  user?: {
    id: number;
    first_name: string;
    last_name: string | null;
    username: string | null;
    phone_number: string;
  };
}

export interface TelegramStatusRequest {
  phone_number: string;
}

export interface TelegramStatusResponse {
  status: "ok";
  authorized: boolean;
  user_info?: {
    id: number;
    first_name: string;
    last_name: string | null;
    username: string | null;
    phone_number: string;
  };
}

export interface TelegramContact {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  phone_number: string;
  is_contact: boolean;
}

export interface TelegramContactsRequest {
  phone_number?: string;
  tg_user_id?: number;
}

export interface TelegramContactsResponse {
  status: "ok" | "error";
  contacts: TelegramContact[];
  error?: string;
}

export interface TelegramSendMessageRequest {
  phone_number: string;
  recipient_id: number | string;
  text: string;
}

export interface TelegramSendMessageResponse {
  status: "ok" | "error";
  success?: boolean;
  message_id?: number;
  date?: string;
  error?: string;
}

// Todoist Integration Types
export interface TodoistAuthSaveRequest {
  user_id: string;
  token: string;
}

export interface TodoistAuthSaveResponse {
  status: "ok" | "error";
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
  status: "ok" | "error";
  task_id?: string;
  content?: string;
  url?: string;
  message?: string;
  error?: string;
}