import { cn } from "@/shared/lib/mergeClass";
import { Copy, ThumbsUp, RefreshCw, Check } from "lucide-react";
import { useModal } from "@/shared/lib/modal/context";
import { EModalVariables } from "@/shared/lib/modal/constants";
import { MarkdownContent } from "./markdownContent";
import { TypingIndicator } from "./typingIndicator";
import { useCopied } from "@/shared/hooks/useCopy";
import { Image } from "@/shared/ui/image/image";
import { useParams } from "react-router-dom";
import { FileMessage } from "./fileMessage";
import { TAG_COLORS } from "../tagSelector/tagSelector";

export interface MessageProps {
  content: string;
  isUser: boolean;
  answerId?: number;
  rating?: number | null;
  isTyping?: boolean;
  file_url?: string;
  isCompact?: boolean;
  tag: string;
}

export const Message = ({
  content,
  isUser,
  answerId,
  tag,
  rating,
  isTyping = false,
  file_url,
  isCompact = false,
}: MessageProps) => {
  const chatId = useParams().chatId;

  const { openModal } = useModal();

  const { handleCopyClick, isCopied } = useCopied();

  const handleLikeClick = () => {
    if (answerId) {
      openModal(EModalVariables.RATING_MODAL, {
        answerId,
        chatId: Number(chatId),
      });
    }
  };

  return (
    <div
      className={cn(
        "flex gap-4 px-4 md:px-8 py-4 md:py-6",
        isUser ? "justify-end" : "justify-start",
        isCompact && "px-4 md:px-4 py-4 md:py-4"
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
          "flex flex-col max-w-[85%] md:max-w-[80%] min-w-0",
          isUser ? "items-end" : "items-start",
          isCompact && "max-w-[85%] md:max-w-[85%]"
        )}
      >
        {!isUser && !isTyping && (
          <div className="mb-2">
            <span
              className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium border"
              style={{
                borderColor: TAG_COLORS[tag as keyof typeof TAG_COLORS],
                backgroundColor:
                  TAG_COLORS[tag as keyof typeof TAG_COLORS] + "20",
                color: TAG_COLORS[tag as keyof typeof TAG_COLORS],
              }}
            >
              {tag}
            </span>
          </div>
        )}
        {file_url && isUser && <FileMessage fileUrl={file_url} />}
        {file_url && isUser && content && content.trim() && (
          <div
            className={cn(
              "rounded-2xl px-4 py-3 text-sm md:text-base leading-relaxed mt-2",
              "bg-red-50 dark:bg-red-500/20 text-foreground rounded-tr-sm border border-red-100 dark:border-red-500/30"
            )}
          >
            {content}
          </div>
        )}
        {!file_url && (
          <div
            className={cn(
              "rounded-2xl text-sm md:text-base leading-relaxed",
              "break-words overflow-wrap-anywhere w-full",
              isUser
                ? "px-4 py-3 bg-red-50 dark:bg-red-500/20 text-foreground rounded-tr-sm border border-red-100 dark:border-red-500/30"
                : "text-foreground rounded-xl dark:border-gray-700",
              isCompact && "text-sm md:text-sm"
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
        )}
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
                !answerId && "opacity-50 cursor-not-allowed"
              )}
              aria-label="Нравится"
              onClick={handleLikeClick}
            >
              <ThumbsUp
                className={cn(
                  "h-4 w-4",
                  rating && rating > 0
                    ? "text-red-600 dark:text-yellow-400"
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
