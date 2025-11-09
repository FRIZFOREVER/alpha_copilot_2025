import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createChat } from "../api/chatService";
import { CreateChatDto, CreateChatResponse } from "../types/types";
import { CREATE_CHAT_QUERY, GET_CHATS_QUERY } from "../lib/constants";

export const useCreateChatMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: [CREATE_CHAT_QUERY],
    mutationFn: (data: CreateChatDto) => createChat(data),
    onSuccess: (data: CreateChatResponse) => {
      // Инвалидируем кеш списка чатов после создания нового чата
      queryClient.invalidateQueries({ queryKey: [GET_CHATS_QUERY] });
      return data;
    },
  });
};

