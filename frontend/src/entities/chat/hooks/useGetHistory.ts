import { useQuery } from "@tanstack/react-query";
import { getHistory } from "../api/chatService";
import { GetHistoryResponse, HistoryMessage } from "../types/types";
import { GET_HISTORY_QUERY } from "../lib/constants";
import type { MessageData, UserMessage, BotMessage } from "@/shared/types/message";

export const useGetHistoryQuery = (chatId: number | undefined) => {
  return useQuery({
    queryKey: [GET_HISTORY_QUERY, chatId],
    queryFn: async (): Promise<GetHistoryResponse> => {
      if (!chatId) {
        throw new Error("Chat ID is required");
      }
      const response = await getHistory(chatId);
      return response;
    },
    enabled: !!chatId,
    select: (data: GetHistoryResponse): MessageData[] => {
      if (!data || data.length === 0) return [];

      const result: MessageData[] = [];

      data.forEach((historyItem: HistoryMessage) => {
        const userMessage: UserMessage = {
          id: `question-${historyItem.question_id}`,
          content: historyItem.question,
          isUser: true,
          timestamp: historyItem.question_time,
          file_url: historyItem.file_url,
          tag: historyItem.tag,
        };
        result.push(userMessage);

        if (
          historyItem.answer_id &&
          historyItem.answer &&
          historyItem.answer.trim() !== ""
        ) {
          const botMessage: BotMessage = {
            id: `answer-${historyItem.answer_id}`,
            content: historyItem.answer,
            isUser: false,
            timestamp: historyItem.answer_time,
            answerId: historyItem.answer_id,
            rating: historyItem.rating,
            tag: !historyItem.tag ? "general" : historyItem.tag,
          };
          result.push(botMessage);
        }
      });

      return result;
    },
  });
};
