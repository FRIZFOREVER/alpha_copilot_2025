import { ScrollArea } from "@/shared/ui/scroll-area";
import { Message } from "../message";
import { ChatEmptyState } from "../chatEmptyState";
import { useScrollBottom } from "@/shared/hooks/useScrollBottom";
import { cn } from "@/shared/lib/mergeClass";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import type { MessageData } from "@/shared/types/message";
import { useChatScroll } from "../../hooks/useChatScroll";
import { ScrollToBottomButton } from "../scrollToBottomButton";

export interface MessageListProps {
  messages: MessageData[];
  isLoading?: boolean;
  isCompact?: boolean;
  onScrollContainerReady?: (ref: React.RefObject<HTMLElement>) => void;
  scrollButtonContainerRef?: React.RefObject<HTMLDivElement | null>;
}

export const MessageList = ({
  messages,
  isLoading = false,
  isCompact = false,
  onScrollContainerReady,
  scrollButtonContainerRef,
}: MessageListProps) => {
  const { contentRef } = useScrollBottom([
    messages.length,
    isLoading ? "loading" : "loaded",
  ]);

  const { isAtBottom, scrollToBottom } = useChatScroll({
    channelId: "chat",
    chatRef: contentRef,
  });

  useEffect(() => {
    if (onScrollContainerReady && contentRef.current) {
      const scrollContainer = contentRef.current
        .firstElementChild as HTMLElement;
      if (scrollContainer) {
        const containerRef = {
          current: scrollContainer,
        } as React.RefObject<HTMLElement>;
        onScrollContainerReady(containerRef);
      }
    }
  }, [onScrollContainerReady, contentRef]);

  const showScrollButton = !isAtBottom && messages.length > 0;
  const [inputHeight, setInputHeight] = useState(0);

  useEffect(() => {
    if (!scrollButtonContainerRef?.current) return;

    const updateInputHeight = () => {
      const container = scrollButtonContainerRef.current;
      if (container) {
        const height = parseInt(
          container.getAttribute("data-input-height") || "0",
          10
        );
        setInputHeight(height);
      }
    };

    updateInputHeight();

    const resizeObserver = new ResizeObserver(() => {
      updateInputHeight();
    });

    if (scrollButtonContainerRef.current) {
      resizeObserver.observe(scrollButtonContainerRef.current);
    }

    const mutationObserver = new MutationObserver(() => {
      updateInputHeight();
    });

    if (scrollButtonContainerRef.current) {
      mutationObserver.observe(scrollButtonContainerRef.current, {
        attributes: true,
        attributeFilter: ["data-input-height"],
      });
    }

    return () => {
      resizeObserver.disconnect();
      mutationObserver.disconnect();
    };
  }, [scrollButtonContainerRef]);

  return (
    <ScrollArea className="flex-1 max-w-[832px] relative" ref={contentRef}>
      <div
        className={cn(
          messages.length === 0 && "h-full flex items-center justify-center"
        )}
      >
        {messages.length === 0 ? (
          <ChatEmptyState isCompact={isCompact} />
        ) : (
          messages.map((message) => (
            <Message
              key={message.id}
              id={message.id}
              isCompact={isCompact}
              content={message.content}
              isUser={message.isUser}
              answerId={message.isUser ? undefined : message.answerId}
              rating={message.isUser ? undefined : message.rating}
              isTyping={message.isUser ? undefined : message.isTyping}
              tag={message.tag}
              file_url={message.isUser ? message.file_url : undefined}
            />
          ))
        )}
      </div>
      {scrollButtonContainerRef?.current &&
        createPortal(
          <div
            className={cn(
              "absolute right-0 md:-right-7 z-50 pointer-events-auto",
              isCompact && "md:-right-3"
            )}
            style={{
              bottom: `${Math.max(24, inputHeight + 4)}px`,
            }}
          >
            <ScrollToBottomButton
              isCompact={isCompact}
              show={showScrollButton}
              onClick={scrollToBottom}
            />
          </div>,
          scrollButtonContainerRef.current
        )}
    </ScrollArea>
  );
};
