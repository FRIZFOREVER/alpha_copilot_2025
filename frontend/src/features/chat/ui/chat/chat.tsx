import { ChatHeader } from "../chatHeader";
import { MessageList, type MessageData } from "../messageList";
import { ChatInput } from "../chatInput";

export interface ChatProps {
  messages?: MessageData[];
  onSendMessage?: (message: string) => void;
  onSendVoice?: (voiceBlob: Blob) => void;
  isLoading?: boolean;
}

export const Chat = ({
  messages = [],
  onSendMessage,
  onSendVoice,
  isLoading = false,
}: ChatProps) => {
  return (
    <div className="flex h-full flex-col bg-white overflow-hidden">
      <ChatHeader />
      <div className="flex-1 overflow-hidden flex justify-center">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>
      <ChatInput
        onSend={onSendMessage}
        onSendVoice={onSendVoice}
        disabled={isLoading}
      />
    </div>
  );
};
