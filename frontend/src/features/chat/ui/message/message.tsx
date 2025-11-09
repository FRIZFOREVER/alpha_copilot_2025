import { cn } from "@/shared/lib/mergeClass";
import { Copy, ThumbsUp, Share2, RefreshCw, MoreVertical } from "lucide-react";
import { useModal } from "@/shared/lib/modal/context";
import { EModalVariables } from "@/shared/lib/modal/constants";
import { MarkdownContent } from "./markdownContent";

export interface MessageProps {
  content: string;
  isUser: boolean;
  answerId?: number;
  rating?: number | null;
}

export const Message = ({
  content,
  isUser,
  answerId,
  rating,
}: MessageProps) => {
  const { openModal } = useModal();

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
      <div
        className={cn(
          "flex flex-col max-w-[85%] md:max-w-[80%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm md:text-base leading-relaxed",
            isUser
              ? "bg-red-50 dark:bg-red-500/20 text-foreground rounded-tr-sm border border-red-100 dark:border-red-500/30"
              : "text-foreground rounded-tl-sm"
          )}
        >
          {isUser ? content : <MarkdownContent content={content} />}
        </div>
        {!isUser && (
          <div className="flex items-center gap-2 ml-3">
            <button
              className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              aria-label="Копировать"
            >
              <Copy className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button
              onClick={handleLikeClick}
              disabled={!answerId}
              className={cn(
                "p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors",
                rating && rating > 0 && "bg-yellow-100 dark:bg-yellow-900/20",
                !answerId && "opacity-50 cursor-not-allowed"
              )}
              aria-label="Нравится"
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
              aria-label="Поделиться"
            >
              <Share2 className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button
              className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              aria-label="Обновить"
            >
              <RefreshCw className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button
              className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              aria-label="Еще"
            >
              <MoreVertical className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
