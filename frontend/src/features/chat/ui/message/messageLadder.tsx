import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
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
}

export const MessageLadder = ({ messages = [] }: MessageLadderProps) => {
  const [isLadderHovered, setIsLadderHovered] = useState(false);

  if (messages.length === 0) {
    return null;
  }

  return (
    <div
      className="group flex flex-col items-center py-4 bg-black/0 text-white absolute right-4 top-1/2 -translate-y-1/2 z-10"
      onMouseEnter={() => setIsLadderHovered(true)}
      onMouseLeave={() => setIsLadderHovered(false)}
    >
      <button
        className="cursor-pointer transition-all duration-200 flex items-center justify-center h-7 w-7 rounded-full text-zinc-600 hover:bg-zinc-100 hover:text-zinc-800 mb-1"
        aria-label="Прокрутить вверх"
      >
        {isLadderHovered && <ChevronUp size={14} />}
      </button>

      <div className="flex flex-col items-center">
        {messages.map((msg, i) => {
          const baseWidth = calcWidth(msg.content, i, messages.length);
          return (
            <div
              key={msg.id}
              className="py-1 flex items-center justify-center cursor-pointer group/bar"
            >
              <div
                className="relative h-[1px] bg-neutral-500 rounded-full transition-all group-hover/bar:bg-red-500 group-hover/bar:scale-x-125 origin-center"
                style={{ width: `${baseWidth}px` }}
              />
            </div>
          );
        })}
      </div>

      <button
        className="cursor-pointer transition-all duration-200 flex items-center justify-center h-7 w-7 rounded-full text-zinc-600 hover:bg-zinc-100 hover:text-zinc-800 mt-1"
        aria-label="Прокрутить вниз"
      >
        {isLadderHovered && <ChevronDown size={14} />}
      </button>
    </div>
  );
};
