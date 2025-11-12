import { ChatHeader } from "../chatHeader";
import { MessageList, type MessageData } from "../messageList";
import { ChatInput } from "../chatInput";
import { type Suggestion } from "../suggestions";

export interface ChatProps {
  messages?: MessageData[];
  onSendMessage?: (data: { message: string; file_url?: string }) => void;
  onSendVoice?: (voiceBlob: Blob) => void;
  isLoading?: boolean;
  suggestions?: Suggestion[];
  hideHeader?: boolean;
  isCompact?: boolean;
}

export const Chat = ({
  messages = [],
  onSendMessage,
  onSendVoice,
  isLoading = false,
  suggestions,
  hideHeader = false,
  isCompact = false,
}: ChatProps) => {
  return (
    <div className="flex h-full flex-col bg-white overflow-hidden">
      {!hideHeader && <ChatHeader />}
      <div className="flex-1 overflow-hidden flex justify-center">
        <MessageList
          messages={messages}
          isLoading={isLoading}
          isCompact={isCompact}
        />
      </div>
      <ChatInput
        onSend={onSendMessage}
        onSendVoice={onSendVoice}
        disabled={isLoading}
        suggestions={suggestions}
        isCompact={isCompact}
      />
    </div>
  );
};
