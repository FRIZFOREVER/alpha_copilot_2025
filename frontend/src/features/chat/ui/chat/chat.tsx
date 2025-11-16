import { memo, useRef, useCallback, useState } from "react";
import { ChatHeader } from "../chatHeader";
import { MessageList } from "../messageList";
import { ChatInput } from "../chatInput";
import { ScrollToBottomButton } from "../scrollToBottomButton";
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
    const [isAtBottom, setIsAtBottom] = useState(true);
    const [scrollToBottomFn, setScrollToBottomFn] = useState<
      (() => void) | null
    >(null);

    const handleScrollContainerReady = useCallback(
      (ref: React.RefObject<HTMLElement>) => {
        if (ref.current) {
          scrollContainerRef.current = ref.current;
        }
      },
      []
    );

    const handleScrollStateChange = useCallback(
      (isAtBottomValue: boolean, scrollToBottom: () => void) => {
        setIsAtBottom(isAtBottomValue);
        setScrollToBottomFn(() => scrollToBottom);
      },
      []
    );

    const showScrollButton = !isAtBottom && messages.length > 0;

    return (
      <div className="flex h-full flex-col bg-white overflow-hidden relative">
        {!hideHeader && <ChatHeader />}
        <div className="flex-1 overflow-hidden flex justify-center relative">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            isCompact={isCompact}
            onScrollContainerReady={handleScrollContainerReady}
            onScrollStateChange={handleScrollStateChange}
          />
          {scrollToBottomFn && (
            <ScrollToBottomButton
              show={showScrollButton}
              onClick={scrollToBottomFn}
            />
          )}
          <MessageLadder messages={messages} />
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
