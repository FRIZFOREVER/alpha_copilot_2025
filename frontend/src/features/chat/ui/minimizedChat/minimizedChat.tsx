import { MessageSquare, Maximize2 } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { useChatCollapse } from "@/shared/lib/chatCollapse";
import { cn } from "@/shared/lib/mergeClass";
import { Chat } from "../chat";
import { useParams, useNavigate } from "react-router-dom";
import { useGetHistoryQuery } from "@/entities/chat/hooks/useGetHistory";
import { useSendMessageMutation } from "@/entities/chat/hooks/useSendMessage";
import { useSendVoiceMutation } from "@/entities/chat/hooks/useSendVoice";
import { useCreateChatMutation } from "@/entities/chat/hooks/useCreateChat";
import { useMemo, useRef, useEffect } from "react";
import type { MessageData } from "../messageList/messageList";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { capitalizeFirst } from "@/shared/lib/utils/userHelpers";
import { type Suggestion } from "../suggestions";

export const MinimizedChat = () => {
  const { isCollapsed, toggleCollapse } = useChatCollapse();
  const params = useParams<{ chatId?: string }>();
  const navigate = useNavigate();
  const chatId = params.chatId ? Number(params.chatId) : undefined;
  const chatIdRef = useRef(chatId);

  const { data: messages = [], isLoading: isLoadingHistory } =
    useGetHistoryQuery(chatId);
  const { mutate: sendMessage, isPending: isSendingMessage } =
    useSendMessageMutation();
  const { mutate: sendVoice, isPending: isSendingVoice } =
    useSendVoiceMutation();
  const { mutate: createChat, isPending: isCreatingChat } =
    useCreateChatMutation();

  const messagesWithTyping = useMemo<MessageData[]>(() => {
    if (!isSendingMessage && !isSendingVoice) return messages;

    const lastMessage = messages[messages.length - 1];
    const hasLastAnswerWithContent =
      lastMessage &&
      !lastMessage.isUser &&
      lastMessage.content &&
      lastMessage.content.trim() !== "";

    if (hasLastAnswerWithContent) {
      return messages;
    }

    const hasTypingIndicator = messages.some((msg) => msg.isTyping);
    if (hasTypingIndicator) return messages;

    return [
      ...messages,
      {
        id: `typing-${chatId || "new"}`,
        content: "",
        isUser: false,
        isTyping: true,
      },
    ];
  }, [messages, isSendingMessage, isSendingVoice, chatId]);

  const handleSendMessage = (data: { message: string; file_url?: string }) => {
    if (!data.message.trim()) return;

    const trimmedMessage = data.message.trim();

    if (!chatId) {
      const truncatedMessage =
        trimmedMessage.length > 50
          ? trimmedMessage.substring(0, 50) + "..."
          : trimmedMessage;
      const chatName = capitalizeFirst(truncatedMessage);

      createChat(
        { name: chatName },
        {
          onSuccess: (chatData) => {
            navigate(
              `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}/${chatData.chat_id}`,
              { replace: true }
            );
            sendMessage({
              chatId: chatData.chat_id,
              sendMessageDto: {
                question: trimmedMessage,
                file_url: data.file_url,
              },
            });
          },
          onError: (error) => {
            console.error("Failed to create chat:", error);
          },
        }
      );
    } else {
      sendMessage({
        chatId,
        sendMessageDto: {
          question: trimmedMessage,
          file_url: data.file_url,
        },
      });
    }
  };

  const handleSendVoice = (voiceBlob: Blob) => {
    const currentChatId = chatIdRef.current;

    if (!currentChatId) {
      createChat(
        { name: "Новый чат" },
        {
          onSuccess: (data) => {
            chatIdRef.current = data.chat_id;
            navigate(
              `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}/${data.chat_id}`,
              { replace: true }
            );
            sendVoice({
              chatId: data.chat_id,
              voiceBlob,
            });
          },
          onError: (error) => {
            console.error("Failed to create chat:", error);
          },
        }
      );
    } else {
      sendVoice({
        chatId: currentChatId,
        voiceBlob,
      });
    }
  };

  useEffect(() => {
    chatIdRef.current = chatId;
  }, [chatId]);

  const mockSuggestions: Suggestion[] = useMemo(
    () => [
      {
        id: "1",
        title: "Design a database schema",
        subtitle: "for an online merch store",
      },
      {
        id: "2",
        title: "Explain airplane",
        subtitle: "to someone 5 years old",
      },
      {
        id: "3",
        title: "Create a marketing plan",
        subtitle: "for a small business",
      },
    ],
    []
  );

  if (!isCollapsed) return null;

  return (
    <div
      className={cn(
        "w-[450px] h-full",
        "bg-white",
        "flex flex-col",
        "transition-all duration-300 ease-in-out",
        "shrink-0",
        "hidden lg:flex"
      )}
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-gray-700" />
          <span className="font-medium text-sm text-gray-900">
            Чат-помощник
          </span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleCollapse}
          className="h-7 w-7 rounded-lg hover:bg-gray-100"
          title="Развернуть чат"
        >
          <Maximize2 className="h-3.5 w-3.5" />
        </Button>
      </div>
      <div className="flex-1 overflow-hidden">
        <Chat
          messages={messagesWithTyping}
          onSendMessage={handleSendMessage}
          onSendVoice={handleSendVoice}
          isLoading={
            isLoadingHistory ||
            isSendingMessage ||
            isSendingVoice ||
            isCreatingChat
          }
          hideHeader={true}
          suggestions={mockSuggestions}
        />
      </div>
    </div>
  );
};
