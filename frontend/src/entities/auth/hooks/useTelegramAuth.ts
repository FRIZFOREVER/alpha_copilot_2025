import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  startTelegramAuth,
  verifyTelegramAuth,
} from "../api/authService";
import {
  TelegramAuthStartRequest,
  TelegramAuthStartResponse,
  TelegramAuthVerifyRequest,
  TelegramAuthVerifyResponse,
} from "../types/types";
import { TELEGRAM_STATUS_QUERY } from "./useTelegramStatus";

export const TELEGRAM_AUTH_START_QUERY = "telegram-auth-start-query";
export const TELEGRAM_AUTH_VERIFY_QUERY = "telegram-auth-verify-query";

export const useTelegramAuthStartMutation = () => {
  return useMutation({
    mutationKey: [TELEGRAM_AUTH_START_QUERY],
    mutationFn: async (
      request: TelegramAuthStartRequest,
    ): Promise<TelegramAuthStartResponse> => {
      const response = await startTelegramAuth(request);
      return response;
    },
  });
};

export const useTelegramAuthVerifyMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: [TELEGRAM_AUTH_VERIFY_QUERY],
    mutationFn: async (
      request: TelegramAuthVerifyRequest,
    ): Promise<TelegramAuthVerifyResponse> => {
      const response = await verifyTelegramAuth(request);
      return response;
    },
    onSuccess: (response) => {
      // Обновляем статус после успешной авторизации по номеру телефона
      if (response.user?.phone_number) {
        queryClient.invalidateQueries({
          queryKey: [TELEGRAM_STATUS_QUERY, response.user.phone_number],
        });
      }
    },
  });
};

