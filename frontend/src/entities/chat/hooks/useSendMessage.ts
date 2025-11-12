import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendMessageStream } from "../api/chatService";
import {
  SendMessageStreamDto,
  GetHistoryResponse,
  HistoryMessage,
} from "../types/types";
import { SEND_MESSAGE_QUERY, GET_HISTORY_QUERY } from "../lib/constants";
import { createStreamCallbacks } from "../lib/createStreamCallbacks";

export const useSendMessageMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: [SEND_MESSAGE_QUERY],
    mutationFn: ({
      chatId,
      sendMessageDto,
    }: {
      chatId: number;
      sendMessageDto: SendMessageStreamDto;
    }): Promise<{ question_id: number; answer_id: number }> => {
      let tempQuestionId: number | undefined;
      let tempAnswerId: number | undefined;

      const currentHistory = queryClient.getQueryData<GetHistoryResponse>([
        GET_HISTORY_QUERY,
        chatId,
      ]);

      if (currentHistory) {
        const tempMessages = currentHistory.filter(
          (item) =>
            item.question_id < 0 &&
            item.answer_id < 0 &&
            item.question === sendMessageDto.question
        );

        if (tempMessages.length > 0) {
          const lastTemp = tempMessages.reduce(
            (latest, current) =>
              current.question_id > latest.question_id ? current : latest,
            tempMessages[0]
          );
          tempQuestionId = lastTemp.question_id;
          tempAnswerId = lastTemp.answer_id;
        }
      }

      return new Promise((resolve, reject) => {
        const callbacks = createStreamCallbacks({
          queryClient,
          chatId,
          sendMessageDto,
          tempQuestionId,
          tempAnswerId,
          onComplete: (initialData) => {
            resolve({
              question_id: initialData.question_id,
              answer_id: initialData.answer_id,
            });
          },
          onError: (error) => {
            reject(error);
          },
        });

        sendMessageStream(chatId, sendMessageDto, {
          onInitial: callbacks.onInitial,
          onChunk: callbacks.onChunk,
          onComplete: callbacks.onComplete,
          onError: callbacks.onStreamError,
        });
      });
    },
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
        voice_url: sendMessageDto.voice_url || "",
        file_url: sendMessageDto.file_url,
        rating: null,
      };

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) return [optimisticQuestion];
          return [...old, optimisticQuestion];
        }
      );

      return {
        previousHistory,
        chatId,
        sendMessageDto,
      };
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
