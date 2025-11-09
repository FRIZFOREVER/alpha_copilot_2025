import { queryClient } from "@/shared/api/queryClient";
import { LoaderFunctionArgs, redirect } from "react-router-dom";
import { getChats, createChat } from "../api/chatService";
import { GetChatsResponse } from "../types/types";
import { GET_CHATS_QUERY } from "../lib/constants";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const chatDetailAction = async ({}: LoaderFunctionArgs) => {
  const loadChats = async (): Promise<GetChatsResponse> => {
    const cached = queryClient.getQueryData<GetChatsResponse>([
      GET_CHATS_QUERY,
    ]);
    if (cached) {
      return cached;
    }

    const response = await getChats();
    const chats = response;

    queryClient.setQueryData([GET_CHATS_QUERY], chats);

    return chats;
  };

  try {
    const chats = await loadChats();

    let chatId: number;

    if (chats && chats.length > 0) {
      const sortedChats = [...chats].sort(
        (a, b) =>
          new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
      );
      chatId = sortedChats[0].chat_id;
    } else {
      const newChat = await createChat({ name: "Новый чат" });
      chatId = newChat.chat_id;

      queryClient.setQueryData<GetChatsResponse>([GET_CHATS_QUERY], (old) => {
        if (!old) return [];
        return [
          ...old,
          {
            chat_id: newChat.chat_id,
            name: "Новый чат",
            create_time: new Date().toISOString(),
          },
        ];
      });
    }

    return redirect(
      `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}/${chatId}`
    );
  } catch (error) {
    console.error("Error in chatDetailAction:", error);
    return redirect(`/${ERouteNames.DASHBOARD_ROUTE}`);
  }
};
