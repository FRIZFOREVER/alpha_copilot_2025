import { cn } from "@/shared/lib/mergeClass";
import { Copy, ThumbsUp, RefreshCw, Check } from "lucide-react";
import { useModal } from "@/shared/lib/modal/context";
import { EModalVariables } from "@/shared/lib/modal/constants";
import { MarkdownContent } from "./markdownContent";
import { TypingIndicator } from "./typingIndicator";
import { useCopied } from "@/shared/hooks/useCopy";
import { Image } from "@/shared/ui/image/image";

export interface MessageProps {
  content: string;
  isUser: boolean;
  answerId?: number;
  rating?: number | null;
  isTyping?: boolean;
}

export const Message = ({
  content,
  isUser,
  answerId,
  rating,
  isTyping = false,
}: MessageProps) => {
  const { openModal } = useModal();

  const { handleCopyClick, isCopied } = useCopied();

  const handleLikeClick = () => {
    if (answerId) {
      openModal(EModalVariables.RATING_MODAL, { answerId });
    }
  };

  return (
    <div
      className={cn(
        "flex gap-4 px-4 md:px-8 py-4 md:py-6",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex-shrink-0">
          <Image
            src="/images/Avatar.png"
            alt="AI Assistant"
            className="h-8 w-8 rounded-full"
          />
        </div>
      )}
      <div
        className={cn(
          "flex flex-col max-w-[85%] md:max-w-[80%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        {!isUser && !isTyping && (
          <div className="mb-2">
            <span className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-teal-50 text-teal-700 border border-teal-100">
              #Law
            </span>
          </div>
        )}
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm md:text-base leading-relaxed",
            isUser
              ? "bg-red-50 dark:bg-red-500/20 text-foreground rounded-tr-sm border border-red-100 dark:border-red-500/30"
              : "text-foreground rounded-xl py-0 px-0 dark:border-gray-700"
          )}
        >
          {isTyping ? (
            <TypingIndicator />
          ) : isUser ? (
            content
          ) : (
            <MarkdownContent content={content} />
          )}
        </div>
        {!isUser && !isTyping && (
          <div className="flex items-center gap-2 mt-1">
            {!isCopied ? (
              <button
                className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer"
                aria-label="Копировать"
                value={content}
                onClick={handleCopyClick}
              >
                <Copy className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              </button>
            ) : (
              <button
                className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                aria-label="Готово"
              >
                <Check className="h-4 w-4 text-green-600 " />
              </button>
            )}
            <button
              disabled={!answerId}
              className={cn(
                "p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer",
                rating && rating > 0 && "bg-yellow-100 dark:bg-yellow-900/20",
                !answerId && "opacity-50 cursor-not-allowed"
              )}
              aria-label="Нравится"
              onClick={handleLikeClick}
            >
              <ThumbsUp
                className={cn(
                  "h-4 w-4",
                  rating && rating > 0
                    ? "text-yellow-600 dark:text-yellow-400"
                    : "text-gray-600 dark:text-gray-400"
                )}
              />
            </button>
            <button
              className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              aria-label="Обновить"
            >
              <RefreshCw className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
