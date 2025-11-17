import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendVoice, sendMessageStream } from "../api/chatService";
import {
  SendVoiceResponse,
  GetHistoryResponse,
  HistoryMessage,
  SendMessageStreamDto,
} from "../types/types";
import { GET_HISTORY_QUERY } from "../lib/constants";
import { createStreamCallbacks } from "../lib/createStreamCallbacks";

interface SendVoiceResult {
  voiceResponse: SendVoiceResponse;
  question_id: number;
  answer_id: number;
}

export const useSendVoiceMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ["send-voice"],
    mutationFn: async ({
      chatId,
      voiceBlob,
      profile,
      mode,
      tag,
    }: {
      chatId: number;
      voiceBlob: Blob;
      profile: SendMessageStreamDto["profile"];
      mode?: SendMessageStreamDto["mode"];
      tag?: SendMessageStreamDto["tag"];
    }): Promise<SendVoiceResult> => {
      const voiceResponse: SendVoiceResponse = await sendVoice(voiceBlob);

      let tempQuestionId: number | undefined;
      let tempAnswerId: number | undefined;

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) return old;

          const processingMessages = old.filter(
            (item) =>
              item.question === "Обработка аудио..." && item.question_id < 0
          );

          if (processingMessages.length === 0) return old;

          const lastProcessingMessage = processingMessages.reduce(
            (latest, current) =>
              current.question_id > latest.question_id ? current : latest,
            processingMessages[0]
          );

          tempQuestionId = lastProcessingMessage.question_id;
          tempAnswerId = lastProcessingMessage.answer_id;

          return old.map((item) => {
            if (
              item.question_id === lastProcessingMessage.question_id &&
              item.answer_id === lastProcessingMessage.answer_id
            ) {
              return {
                ...item,
                question: voiceResponse.question,
                voice_url: voiceResponse.voice_url,
              };
            }
            return item;
          });
        }
      );

      const sendMessageDto: SendMessageStreamDto = {
        question: voiceResponse.question,
        voice_url: voiceResponse.voice_url,
        mode: mode,
        tag: tag ?? "general",
        profile,
      };

      return new Promise((resolve, reject) => {
        const callbacks = createStreamCallbacks({
          queryClient,
          chatId,
          sendMessageDto,
          tempQuestionId,
          tempAnswerId,
          onComplete: (initialData) => {
            resolve({
              voiceResponse,
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
    onMutate: async ({ chatId, tag }) => {
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
        question: "Обработка аудио...",
        answer: "",
        question_time: new Date().toISOString(),
        answer_time: new Date().toISOString(),
        voice_url: "",
        rating: null,
        tag: tag ?? "general",
      };

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) return [optimisticMessage];
          return [...old, optimisticMessage];
        }
      );

      return {
        previousHistory,
        chatId,
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
