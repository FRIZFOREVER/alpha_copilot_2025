import { useQuery } from "@tanstack/react-query";
import { getChats } from "../api/chatService";
import { GetChatsResponse } from "../types/types";
import { GET_CHATS_QUERY } from "../lib/constants";

export const useGetChatsQuery = () => {
  return useQuery({
    queryKey: [GET_CHATS_QUERY],
    queryFn: async (): Promise<GetChatsResponse> => {
      const response = await getChats();
      return response;
    },
  });
};
