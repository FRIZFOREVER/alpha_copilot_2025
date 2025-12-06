import { QueryClient } from "@tanstack/react-query";
import {
  GetHistoryResponse,
  HistoryMessage,
  StreamInitialResponse,
  StreamChunk,
  SendMessageStreamDto,
} from "../types/types";
import { GET_HISTORY_QUERY } from "../lib/constants";

interface CreateStreamCallbacksParams {
  queryClient: QueryClient;
  chatId: number;
  sendMessageDto: SendMessageStreamDto;
  tempQuestionId?: number;
  tempAnswerId?: number;
  onComplete?: (initialData: StreamInitialResponse) => void;
  onError?: (error: Error) => void;
}

export const createStreamCallbacks = ({
  queryClient,
  chatId,
  sendMessageDto,
  tempQuestionId,
  tempAnswerId,
  onComplete,
  onError,
}: CreateStreamCallbacksParams) => {
  let initialData: StreamInitialResponse | null = null;

  return {
    onInitial: (data: StreamInitialResponse) => {
      initialData = data;

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          const newMessage: HistoryMessage = {
            question_id: data.question_id,
            answer_id: data.answer_id,
            question: sendMessageDto.question,
            answer: "",
            question_time: data.question_time,
            answer_time: data.question_time,
            voice_url: sendMessageDto.voice_url || "",
            question_file_url: sendMessageDto.file_url,
            answer_file_url: data.file_url || undefined,
            rating: null,
            tag: sendMessageDto.tag || "general",
          };

          if (!old) {
            return [newMessage];
          }

          const filtered = old.filter(
            (item) =>
              !(
                tempQuestionId &&
                tempAnswerId &&
                item.question_id === tempQuestionId &&
                item.answer_id === tempAnswerId
              ) &&
              item.question_id !== data.question_id &&
              item.answer_id !== data.answer_id
          );

          return [...filtered, newMessage];
        }
      );
    },
    onChunk: (chunk: StreamChunk) => {
      if (!initialData || !chunk.content) return;

      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) return old;
          let hasChanges = false;
          const updated = old.map((item) => {
            if (
              item.question_id === initialData!.question_id &&
              item.answer_id === initialData!.answer_id
            ) {
              hasChanges = true;
              const newAnswer = (item.answer || "") + chunk.content;
              return {
                ...item,
                answer: newAnswer,
                answer_time: chunk.time,
              };
            }
            return item;
          });

          return hasChanges ? updated : old;
        }
      );
    },
    onComplete: () => {
      if (initialData) {
        onComplete?.(initialData);
      }
    },
    onStreamError: (error: Error) => {
      queryClient.setQueryData<GetHistoryResponse>(
        [GET_HISTORY_QUERY, chatId],
        (old) => {
          if (!old) return old;
          return old.filter(
            (item) =>
              item.question_id !== initialData?.question_id &&
              item.answer_id !== initialData?.answer_id
          );
        }
      );
      onError?.(error);
    },
    getInitialData: () => initialData,
  };
};
