export type ApiStatus = "ok" | "error";

export type TelegramAuthStatus = ApiStatus | "code_sent" | "password_required";

export interface BaseApiResponse<T = unknown> {
  status: ApiStatus;
  message?: string;
  error?: string;
  data?: T;
}

export interface SuccessApiResponse<T = unknown> extends BaseApiResponse<T> {
  status: "ok";
}

export interface ErrorApiResponse extends BaseApiResponse {
  status: "error";
  error: string;
}

export type ApiResponse<T = unknown> = SuccessApiResponse<T> | ErrorApiResponse;

