import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendVoice, sendMessage } from "../api/chatService";
import {
  SendVoiceResponse,
  SendMessageResponse,
  GetHistoryResponse,
  HistoryMessage,
} from "../types/types";
import { GET_HISTORY_QUERY } from "../lib/constants";

interface SendVoiceResult {
  voiceResponse: SendVoiceResponse;
  messageResponse: SendMessageResponse;
}

export const useSendVoiceMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ["send-voice"],
    mutationFn: async ({
      chatId,
      voiceBlob,
    }: {
      chatId: number;
      voiceBlob: Blob;
    }): Promise<SendVoiceResult> => {
      const voiceResponse: SendVoiceResponse = await sendVoice(voiceBlob);

      const messageResponse = await sendMessage(chatId, {
        question: voiceResponse.question,
      });

      return { voiceResponse, messageResponse };
    },
    onMutate: async ({ chatId }) => {
      await queryClient.cancelQueries({
        queryKey: [GET_HISTORY_QUERY, chatId],
      });

      const previousHistory = queryClient.getQueryData<GetHistoryResponse>([
        GET_HISTORY_QUERY,
        chatId,
      ]);

      const tempQuestionId = -Date.now();
      const tempAnswerId = tempQuestionId - 1;

      const optimisticMessage: HistoryMessage = {
        question_id: tempQuestionId,
        answer_id: tempAnswerId,
        question: "обработка аудио",
        answer: "",
        question_time: new Date().toISOString(),
        answer_time: new Date().toISOString(),
        voice_url: "",
        rating: null,
      };

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) return [optimisticMessage];
          return [...old, optimisticMessage];
        }
      );

      return { previousHistory, chatId, tempQuestionId, tempAnswerId };
    },
    onSuccess: (data: SendVoiceResult, _, context) => {
      if (!context) return;

      const { chatId, tempQuestionId, tempAnswerId } = context;
      const { voiceResponse, messageResponse } = data;

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) {
            const newHistoryItem: HistoryMessage = {
              question_id: messageResponse.question_id,
              answer_id: messageResponse.answer_id,
              question: voiceResponse.question,
              answer: messageResponse.answer,
              question_time: messageResponse.question_time,
              answer_time: messageResponse.answer_time,
              voice_url: voiceResponse.voice_url,
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
            question_id: messageResponse.question_id,
            answer_id: messageResponse.answer_id,
            question: voiceResponse.question,
            answer: messageResponse.answer,
            question_time: messageResponse.question_time,
            answer_time: messageResponse.answer_time,
            voice_url: voiceResponse.voice_url,
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
