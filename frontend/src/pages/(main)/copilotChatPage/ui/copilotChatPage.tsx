import { Chat } from "@/features/chat";
import { useParams } from "react-router-dom";
import { useGetHistoryQuery } from "@/entities/chat/hooks/useGetHistory";
import { useSendMessageMutation } from "@/entities/chat/hooks/useSendMessage";
import { useSendVoiceMutation } from "@/entities/chat/hooks/useSendVoice";
import { useMemo } from "react";
import type { MessageData } from "@/features/chat/ui/messageList/messageList";

const CopilotChatPage = () => {
  const params = useParams<{ chatId?: string }>();
  const chatId = params.chatId ? parseInt(params.chatId, 10) : undefined;

  const { data: messages = [], isLoading: isLoadingHistory } =
    useGetHistoryQuery(chatId);
  const { mutate: sendMessage, isPending: isSendingMessage } =
    useSendMessageMutation();
  const { mutate: sendVoice, isPending: isSendingVoice } =
    useSendVoiceMutation();

  const messagesWithTyping = useMemo<MessageData[]>(() => {
    if (!isSendingMessage && !isSendingVoice) return messages;

    const hasTypingIndicator = messages.some((msg) => msg.isTyping);
    if (hasTypingIndicator) return messages;

    return [
      ...messages,
      {
        id: `typing-${chatId}`,
        content: "",
        isUser: false,
        isTyping: true,
      },
    ];
  }, [messages, isSendingMessage, isSendingVoice, chatId]);

  const handleSendMessage = (message: string) => {
    if (!chatId || !message.trim()) return;

    sendMessage({
      chatId,
      sendMessageDto: { question: message.trim() },
    });
  };

  const handleSendVoice = (voiceBlob: Blob) => {
    if (!chatId) return;

    sendVoice({
      chatId,
      voiceBlob,
    });
  };

  return (
    <Chat
      messages={messagesWithTyping}
      onSendMessage={handleSendMessage}
      onSendVoice={handleSendVoice}
      isLoading={isLoadingHistory || isSendingMessage || isSendingVoice}
    />
  );
};
export default CopilotChatPage;
