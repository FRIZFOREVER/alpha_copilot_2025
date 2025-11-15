import { useQuery } from "@tanstack/react-query";
import { getTelegramContacts } from "../api/authService";
import { TelegramContactsResponse, TelegramContactsRequest } from "../types/types";

export const TELEGRAM_CONTACTS_QUERY = "telegram-contacts-query";

export const useTelegramContactsQuery = (
  request: TelegramContactsRequest | undefined
) => {
  return useQuery({
    queryKey: [
      TELEGRAM_CONTACTS_QUERY,
      request?.tg_user_id,
      request?.phone_number,
    ],
    queryFn: async (): Promise<TelegramContactsResponse> => {
      if (!request || (!request.phone_number && !request.tg_user_id)) {
        throw new Error("Phone number or tg_user_id is required");
      }
      const response = await getTelegramContacts(request);
      return response;
    },
    enabled: !!request && (!!request.phone_number || !!request.tg_user_id),
    retry: false,
  });
};

