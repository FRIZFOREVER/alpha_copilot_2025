import { useMutation, useQueryClient } from "@tanstack/react-query";
import { likeMessage } from "../api/chatService";
import { LikeMessageDto, LikeMessageResponse } from "../types/types";
import { LIKE_MESSAGE_QUERY, GET_HISTORY_QUERY } from "../lib/constants";

export const useLikeMessageMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: [LIKE_MESSAGE_QUERY],
    mutationFn: ({
      chatId,
      likeDto,
    }: {
      chatId: number;
      likeDto: LikeMessageDto;
    }) => likeMessage(chatId, likeDto),
    onSuccess: (data: LikeMessageResponse) => {
      queryClient.invalidateQueries({ queryKey: [GET_HISTORY_QUERY] });
      return data;
    },
  });
};
