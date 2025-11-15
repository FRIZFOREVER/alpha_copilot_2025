import { useParams, useNavigate } from "react-router-dom";
import { useGetHistoryQuery } from "@/entities/chat/hooks/useGetHistory";
import { useSendMessageMutation } from "@/entities/chat/hooks/useSendMessage";
import { useSendVoiceMutation } from "@/entities/chat/hooks/useSendVoice";
import { useCreateChatMutation } from "@/entities/chat/hooks/useCreateChat";
import { useMemo, useRef, useEffect, useState } from "react";
import type { MessageData } from "../ui/messageList/messageList";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { capitalizeFirst } from "@/shared/lib/utils/userHelpers";
import { type Suggestion } from "../ui/suggestions";
import { type TagId } from "../ui/tagSelector/tagSelector";
import { TelegramContact } from "@/entities/auth/types/types";
import { useModal } from "@/shared/lib/modal/context";
import { EModalVariables } from "@/shared/lib/modal/constants";
import { useTelegramStatusQuery } from "@/entities/auth/hooks/useTelegramStatus";

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

export const useChatMessages = () => {
  const params = useParams<{ chatId?: string }>();
  const navigate = useNavigate();
  const { openModal } = useModal();
  const chatId = params.chatId ? Number(params.chatId) : undefined;
  const chatIdRef = useRef(chatId);
  const [selectedTelegramContact, setSelectedTelegramContact] =
    useState<TelegramContact | null>(null);

  // Получаем номер телефона из localStorage
  const getStoredPhoneNumber = (): string | undefined => {
    try {
      const stored = localStorage.getItem("telegram_phone_number");
      return stored || undefined;
    } catch {
      return undefined;
    }
  };

  const phone_number = getStoredPhoneNumber();
  const { data: telegramStatus } = useTelegramStatusQuery(phone_number);

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

  const handleSelectTelegramContact = () => {
    if (!telegramStatus?.authorized) {
      // Если не авторизован, можно показать сообщение
      console.warn("Telegram not authorized. Please authorize first.");
      return;
    }

    // Используем tg_user_id из user_info, если доступен
    const tg_user_id = telegramStatus?.user_info?.id;
    const request_data = tg_user_id
      ? { tg_user_id }
      : phone_number
        ? { phone_number }
        : null;

    if (!request_data) {
      console.warn("No phone_number or tg_user_id available");
      return;
    }

    openModal(EModalVariables.TELEGRAM_CONTACTS_MODAL, {
      ...request_data,
      onSelect: (contact: TelegramContact) => {
        setSelectedTelegramContact(contact);
      },
    });
  };

  const handleSendMessage = (data: {
    message: string;
    file_url?: string;
    tag?: TagId;
  }) => {
    if (!data.message.trim()) return;

    const trimmedMessage = data.message.trim();
    const tag = data.tag || "";

    const sendMessageDto = {
      question: trimmedMessage,
      file_url: data.file_url,
      tag: tag,
      mode: "fast" as const,
      send_to_telegram: !!selectedTelegramContact,
      phone_number: selectedTelegramContact ? phone_number : undefined,
      recipient_id: selectedTelegramContact
        ? selectedTelegramContact.id
        : undefined,
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
            navigate(
              `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}/${chatData.chat_id}`,
              { replace: true },
            );
            sendMessage({
              chatId: chatData.chat_id,
              sendMessageDto,
            });
            // Сбрасываем выбранный контакт после отправки
            setSelectedTelegramContact(null);
          },
          onError: (error) => {
            console.error("Failed to create chat:", error);
          },
        },
      );
    } else {
      sendMessage({
        chatId,
        sendMessageDto,
      });
      // Сбрасываем выбранный контакт после отправки
      setSelectedTelegramContact(null);
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
              { replace: true },
            );
            sendVoice({
              chatId: data.chat_id,
              voiceBlob,
            });
          },
          onError: (error) => {
            console.error("Failed to create chat:", error);
          },
        },
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

  const suggestions: Suggestion[] = useMemo(() => DEFAULT_SUGGESTIONS, []);

  const isLoading =
    isLoadingHistory || isSendingMessage || isSendingVoice || isCreatingChat;

  return {
    messages: messagesWithTyping,
    handleSendMessage,
    handleSendVoice,
    isLoading,
    suggestions,
    chatId,
    selectedTelegramContact,
    handleSelectTelegramContact,
    isTelegramAuthorized: telegramStatus?.authorized || false,
  };
};
