import { Chat } from "@/features/chat";
import { useParams, useNavigate } from "react-router-dom";
import { useGetHistoryQuery } from "@/entities/chat/hooks/useGetHistory";
import { useSendMessageMutation } from "@/entities/chat/hooks/useSendMessage";
import { useSendVoiceMutation } from "@/entities/chat/hooks/useSendVoice";
import { useCreateChatMutation } from "@/entities/chat/hooks/useCreateChat";
import { useMemo, useRef, useEffect } from "react";
import type { MessageData } from "@/features/chat/ui/messageList/messageList";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { capitalizeFirst } from "@/shared/lib/utils/userHelpers";
import { type Suggestion } from "@/features/chat/ui/suggestions";

const CopilotChatPage = () => {
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

  const handleSendMessage = (message: string) => {
    if (!message.trim()) return;

    const trimmedMessage = message.trim();

    if (!chatId) {
      const truncatedMessage =
        trimmedMessage.length > 50
          ? trimmedMessage.substring(0, 50) + "..."
          : trimmedMessage;
      const chatName = capitalizeFirst(truncatedMessage);

      createChat(
        { name: chatName },
        {
          onSuccess: (data) => {
            navigate(
              `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}/${data.chat_id}`,
              { replace: true }
            );
            sendMessage({
              chatId: data.chat_id,
              sendMessageDto: { question: trimmedMessage },
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
        sendMessageDto: { question: trimmedMessage },
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
      // {
      //   id: "4",
      //   title: "Write a business proposal",
      //   subtitle: "for a new product launch",
      // },
      // {
      //   id: "5",
      //   title: "Analyze financial data",
      //   subtitle: "and provide insights",
      // },
    ],
    []
  );

  return (
    <Chat
      messages={messagesWithTyping}
      onSendMessage={handleSendMessage}
      onSendVoice={handleSendVoice}
      isLoading={
        isLoadingHistory || isSendingMessage || isSendingVoice || isCreatingChat
      }
      suggestions={mockSuggestions}
    />
  );
};
export default CopilotChatPage;
