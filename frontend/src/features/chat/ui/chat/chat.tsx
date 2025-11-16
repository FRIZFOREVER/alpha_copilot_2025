import { memo, useRef, useCallback } from "react";
import { ChatHeader } from "../chatHeader";
import { MessageList } from "../messageList";
import { ChatInput } from "../chatInput";
import { type Suggestion } from "../suggestions";
import type { MessageData } from "@/shared/types/message";
import { MessageLadder } from "../message/messageLadder";

export interface ChatProps {
  messages?: MessageData[];
  onSendMessage?: (data: { message: string; file_url?: string }) => void;
  onSendVoice?: (voiceBlob: Blob) => void;
  isLoading?: boolean;
  suggestions?: Suggestion[];
  hideHeader?: boolean;
  isCompact?: boolean;
}

export const Chat = memo(
  ({
    messages = [],
    onSendMessage,
    onSendVoice,
    isLoading = false,
    suggestions,
    hideHeader = false,
    isCompact = false,
  }: ChatProps) => {
    const scrollContainerRef = useRef<HTMLElement | null>(null);

    const handleScrollContainerReady = useCallback(
      (ref: React.RefObject<HTMLElement>) => {
        if (ref.current) {
          scrollContainerRef.current = ref.current;
        }
      },
      []
    );

    return (
      <div className="flex h-full flex-col bg-white overflow-hidden relative">
        {!hideHeader && <ChatHeader />}
        <div className="flex-1 overflow-hidden flex justify-center relative">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            isCompact={isCompact}
            onScrollContainerReady={handleScrollContainerReady}
          />
          {!isCompact && (
            <MessageLadder
              messages={messages}
              scrollContainerRef={scrollContainerRef}
            />
          )}
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
  }
);

Chat.displayName = "Chat";
