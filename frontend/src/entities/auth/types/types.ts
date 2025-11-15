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