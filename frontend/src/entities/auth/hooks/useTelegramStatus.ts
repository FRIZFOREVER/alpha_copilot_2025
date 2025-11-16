import { useQuery } from "@tanstack/react-query";
import { getTelegramStatus } from "../api/authService";
import { TelegramStatusResponse } from "../types/types";

export const TELEGRAM_STATUS_QUERY = "telegram-status-query";

export const useTelegramStatusQuery = (phone_number: string | undefined) => {
  return useQuery({
    queryKey: [TELEGRAM_STATUS_QUERY, phone_number],
    queryFn: async (): Promise<TelegramStatusResponse> => {
      if (!phone_number) {
        throw new Error("Phone number is required");
      }
      const response = await getTelegramStatus({ phone_number });
      return response;
    },
    enabled: !!phone_number,
    retry: false,
  });
};
