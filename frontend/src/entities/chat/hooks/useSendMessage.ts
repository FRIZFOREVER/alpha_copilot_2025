import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendMessage } from "../api/chatService";
import {
  SendMessageDto,
  SendMessageResponse,
  GetHistoryResponse,
  HistoryMessage,
} from "../types/types";
import { SEND_MESSAGE_QUERY, GET_HISTORY_QUERY } from "../lib/constants";

export const useSendMessageMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: [SEND_MESSAGE_QUERY],
    mutationFn: ({
      chatId,
      sendMessageDto,
    }: {
      chatId: number;
      sendMessageDto: SendMessageDto;
    }) => sendMessage(chatId, sendMessageDto),
    onMutate: async ({ chatId, sendMessageDto }) => {
      await queryClient.cancelQueries({
        queryKey: [GET_HISTORY_QUERY, chatId],
      });

      const previousHistory = queryClient.getQueryData<GetHistoryResponse>([
        GET_HISTORY_QUERY,
        chatId,
      ]);

      const tempQuestionId = -Date.now();
      const tempAnswerId = tempQuestionId - 1;

      const optimisticQuestion: HistoryMessage = {
        question_id: tempQuestionId,
        answer_id: tempAnswerId,
        question: sendMessageDto.question,
        answer: "",
        question_time: new Date().toISOString(),
        answer_time: new Date().toISOString(),
        voice_url: "",
        rating: null,
      };

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) return [optimisticQuestion];
          return [...old, optimisticQuestion];
        }
      );

      return { previousHistory, chatId, tempQuestionId, tempAnswerId };
    },
    onSuccess: (data: SendMessageResponse, variables, context) => {
      if (!context) return;

      const { chatId, tempQuestionId, tempAnswerId } = context;

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) {
            const newHistoryItem: HistoryMessage = {
              question_id: data.question_id,
              answer_id: data.answer_id,
              question: variables.sendMessageDto.question,
              answer: data.answer,
              question_time: data.question_time,
              answer_time: data.answer_time,
              voice_url: "",
              rating: null,
            };
            return [newHistoryItem];
          }

          const filtered = old.filter(
            (item) =>
              item.question_id !== tempQuestionId &&
              item.answer_id !== tempAnswerId
          );

          const newHistoryItem: HistoryMessage = {
            question_id: data.question_id,
            answer_id: data.answer_id,
            question: variables.sendMessageDto.question,
            answer: data.answer,
            question_time: data.question_time,
            answer_time: data.answer_time,
            voice_url: "",
            rating: null,
          };

          return [...filtered, newHistoryItem];
        }
      );
    },
    onError: (_error, _variables, context) => {
      if (context?.previousHistory !== undefined && context?.chatId) {
        queryClient.setQueryData(
          [GET_HISTORY_QUERY, context.chatId],
          context.previousHistory
        );
      }
    },
  });
};
