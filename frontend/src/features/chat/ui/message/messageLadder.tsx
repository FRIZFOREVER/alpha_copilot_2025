import { ChevronDown, ChevronUp } from "lucide-react";
import { useState, useCallback, useEffect } from "react";
import type { MessageData } from "@/shared/types/message";

const calcWidth = (text: string, index: number, total: number) => {
  const minWidth = 2;
  const maxWidth = 16;

  const textLength = text.length;
  const logLength = Math.log(textLength + 1);
  const maxLogLength = Math.log(200);

  const normalizedLength = Math.min(1, logLength / maxLogLength);

  const positionFactor = Math.sin((index / (total - 1 || 1)) * Math.PI);

  const combinedFactor = normalizedLength * 0.7 + positionFactor * 0.3;

  const width = minWidth + (maxWidth - minWidth) * combinedFactor;

  return Math.round(width);
};

export interface MessageLadderProps {
  messages?: MessageData[];
  scrollContainerRef?: React.RefObject<HTMLElement | null>;
}

const truncateText = (text: string, maxLength: number = 100) => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
};

export const MessageLadder = ({
  messages = [],
  scrollContainerRef,
}: MessageLadderProps) => {
  const [isLadderHovered, setIsLadderHovered] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [hoveredBarIndex, setHoveredBarIndex] = useState<number | null>(null);

  useEffect(() => {
    setSelectedIndex(0);
  }, [messages.length]);

  const scrollToMessage = useCallback(
    (messageId: string) => {
      if (!scrollContainerRef?.current) return;

      const scrollContainer = scrollContainerRef.current
        .firstElementChild as HTMLElement;
      if (!scrollContainer) return;

      const messageElement = scrollContainer.querySelector(
        `[data-message-id="${messageId}"]`
      ) as HTMLElement;

      if (messageElement) {
        messageElement.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      }
    },
    [scrollContainerRef]
  );

  const handleBarClick = useCallback(
    (messageId: string, index: number) => {
      setSelectedIndex(index);
      scrollToMessage(messageId);
    },
    [scrollToMessage]
  );

  const handleScrollUp = useCallback(() => {
    if (selectedIndex > 0) {
      const newIndex = selectedIndex - 1;
      setSelectedIndex(newIndex);
      scrollToMessage(messages[newIndex].id);
    }
  }, [selectedIndex, messages, scrollToMessage]);

  const handleScrollDown = useCallback(() => {
    if (selectedIndex < messages.length - 1) {
      const newIndex = selectedIndex + 1;
      setSelectedIndex(newIndex);
      scrollToMessage(messages[newIndex].id);
    }
  }, [selectedIndex, messages, scrollToMessage]);

  if (messages.length <= 3) {
    return null;
  }

  return (
    <div
      className="hidden md:flex group flex-col items-center py-4 bg-black/0 text-white absolute right-2 top-1/2 -translate-y-1/2 z-10"
      onMouseEnter={() => setIsLadderHovered(true)}
      onMouseLeave={() => setIsLadderHovered(false)}
    >
      <button
        onClick={handleScrollUp}
        disabled={selectedIndex === 0}
        className="cursor-pointer transition-all duration-200 flex items-center justify-center h-7 w-7 rounded-full text-zinc-600 hover:bg-zinc-100 hover:text-zinc-800 mb-1 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Прокрутить вверх"
      >
        {isLadderHovered && <ChevronUp size={14} />}
      </button>

      <div className="flex flex-col items-center relative">
        {messages.map((msg, i) => {
          const baseWidth = calcWidth(msg.content, i, messages.length);
          const isSelected = selectedIndex === i;
          const isHovered = hoveredBarIndex === i;
          return (
            <div
              key={msg.id}
              onClick={() => handleBarClick(msg.id, i)}
              onMouseEnter={() => setHoveredBarIndex(i)}
              onMouseLeave={() => setHoveredBarIndex(null)}
              className="py-1 flex items-center justify-center cursor-pointer group/bar relative"
            >
              {isHovered && (
                <div className="absolute right-full mr-3 w-64 max-h-24 bg-white rounded-3xl shadow-lg border border-gray-200 p-3 flex flex-col z-50 top-1/2 -translate-y-1/2">
                  {!msg.isUser && (
                    <div className="text-xs font-medium text-gray-500 mb-1.5 flex-shrink-0">
                      FinAI
                    </div>
                  )}
                  <div className="text-sm text-gray-800 overflow-hidden break-words">
                    {truncateText(msg.content, 150)}
                  </div>
                </div>
              )}
              <div
                className={`relative h-[1px] rounded-full transition-all group-hover/bar:bg-red-500 group-hover/bar:scale-x-125 origin-center ${
                  isSelected ? "bg-red-500" : "bg-neutral-500"
                }`}
                style={{ width: `${baseWidth}px` }}
              />
            </div>
          );
        })}
      </div>

      <button
        onClick={handleScrollDown}
        disabled={selectedIndex === messages.length - 1}
        className="cursor-pointer transition-all duration-200 flex items-center justify-center h-7 w-7 rounded-full text-zinc-600 hover:bg-zinc-100 hover:text-zinc-800 mt-1 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Прокрутить вниз"
      >
        {isLadderHovered && <ChevronDown size={14} />}
      </button>
    </div>
  );
};
