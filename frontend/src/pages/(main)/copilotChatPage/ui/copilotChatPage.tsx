import { memo } from "react";
import { Chat } from "@/features/chat";
import { useChatMessages } from "@/features/chat/hooks/useChatMessages";

const CopilotChatPage = memo(() => {
  const {
    messages,
    handleSendMessage,
    handleSendVoice,
    isLoading,
    suggestions,
  } = useChatMessages();

  return (
    <Chat
      messages={messages}
      onSendMessage={handleSendMessage}
      onSendVoice={handleSendVoice}
      isLoading={isLoading}
      suggestions={suggestions}
    />
  );
});

CopilotChatPage.displayName = "CopilotChatPage";

export default CopilotChatPage;
