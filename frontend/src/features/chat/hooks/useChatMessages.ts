import { useParams, useNavigate } from "react-router-dom";
import { useGetHistoryQuery } from "@/entities/chat/hooks/useGetHistory";
import { useSendMessageMutation } from "@/entities/chat/hooks/useSendMessage";
import { useSendVoiceMutation } from "@/entities/chat/hooks/useSendVoice";
import { useCreateChatMutation } from "@/entities/chat/hooks/useCreateChat";
import { useMemo, useRef, useEffect, useCallback } from "react";
import type { MessageData, BotMessage } from "@/shared/types/message";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { capitalizeFirst } from "@/shared/lib/utils/userHelpers";
import { type Suggestion } from "../ui/suggestions";
import { type TagId } from "../ui/tagSelector/tagSelector";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import { SendMessageStreamDto } from "@/entities/chat/types";
import { useSelectedModel } from "@/shared/hooks/useSelectedModel";
import {
  mapUIModelToMode,
  ModelMode,
  SELECTED_MODEL_STORAGE_KEY,
} from "@/shared/types/modelMode";

const DEFAULT_SUGGESTIONS: Suggestion[] = [
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
];

const CHAT_ROUTE_PREFIX = `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}`;

export const useChatMessages = () => {
  const { data: profile } = useGetProfileQuery();
  const { selectedModel } = useSelectedModel();
  const params = useParams<{ chatId?: string }>();
  const navigate = useNavigate();
  const chatId = useMemo(
    () => (params.chatId ? Number(params.chatId) : undefined),
    [params.chatId]
  );
  const chatIdRef = useRef(chatId);

  const modelMode = useMemo(
    () => mapUIModelToMode(selectedModel),
    [selectedModel]
  );

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

    const hasTypingIndicator = messages.some(
      (msg) => !msg.isUser && msg.isTyping
    );
    if (hasTypingIndicator) return messages;

    const typingMessage: BotMessage = {
      id: `typing-${chatId || "new"}`,
      content: "",
      tag: "general",
      isUser: false,
      isTyping: true,
    };
    return [...messages, typingMessage];
  }, [messages, isSendingMessage, isSendingVoice, chatId]);

  const handleSendMessage = useCallback(
    (data: { message: string; file_url?: string; tag?: TagId }) => {
      if (!data.message.trim() || !profile) return;
      const trimmedMessage = data.message.trim();
      const tag = data.tag || "";
      console.log(localStorage.getItem(SELECTED_MODEL_STORAGE_KEY));
      const sendMessageDto: SendMessageStreamDto = {
        question: trimmedMessage,
        file_url: data.file_url,
        tag: tag,
        mode: localStorage.getItem(SELECTED_MODEL_STORAGE_KEY) as ModelMode,
        profile: {
          id: profile.id,
          fio: profile.username,
          login: profile.login,
          additional_instructions: profile.additional_instructions,
          business_info: profile.business_info,
          user_info: profile.user_info,
        },
      };

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
              navigate(`${CHAT_ROUTE_PREFIX}/${chatData.chat_id}`, {
                replace: true,
              });
              sendMessage({
                chatId: chatData.chat_id,
                sendMessageDto,
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
          sendMessageDto,
        });
      }
    },
    [chatId, createChat, navigate, sendMessage, modelMode, profile]
  );

  const handleSendVoice = useCallback(
    (voiceBlob: Blob, tag?: TagId) => {
      if (!profile) return;
      const currentChatId = chatIdRef.current;
      if (!currentChatId) {
        createChat(
          { name: "Новый чат" },
          {
            onSuccess: (data) => {
              chatIdRef.current = data.chat_id;
              navigate(`${CHAT_ROUTE_PREFIX}/${data.chat_id}`, {
                replace: true,
              });
              sendVoice({
                chatId: data.chat_id,
                voiceBlob,
                profile: {
                  id: profile.id,
                  fio: profile.username,
                  login: profile.login,
                  additional_instructions: profile.additional_instructions,
                  business_info: profile.business_info,
                  user_info: profile.user_info,
                },
                tag: tag,
                mode: localStorage.getItem(
                  SELECTED_MODEL_STORAGE_KEY
                ) as ModelMode,
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
          profile: {
            id: profile.id,
            fio: profile.username,
            login: profile.login,
            additional_instructions: profile.additional_instructions,
            business_info: profile.business_info,
            user_info: profile.user_info,
          },
          tag: tag,
          mode: localStorage.getItem(SELECTED_MODEL_STORAGE_KEY) as ModelMode,
        });
      }
    },
    [createChat, navigate, sendVoice, modelMode, profile]
  );

  useEffect(() => {
    chatIdRef.current = chatId;
  }, [chatId]);

  const suggestions: Suggestion[] = useMemo(() => DEFAULT_SUGGESTIONS, []);

  const isLoading = useMemo(
    () =>
      isLoadingHistory || isSendingMessage || isSendingVoice || isCreatingChat,
    [isLoadingHistory, isSendingMessage, isSendingVoice, isCreatingChat]
  );

  return {
    messages: messagesWithTyping,
    handleSendMessage,
    handleSendVoice,
    isLoading,
    suggestions,
    chatId,
  };
};
