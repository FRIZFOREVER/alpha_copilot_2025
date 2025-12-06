import { cn } from "@/shared/lib/mergeClass";
import {
  Copy,
  ThumbsUp,
  RefreshCw,
  Check,
  Send,
  CheckSquare,
} from "lucide-react";
import { useModal } from "@/shared/lib/modal/context";
import { EModalVariables } from "@/shared/lib/modal/constants";
import { MarkdownContent } from "./markdownContent";
import { TypingIndicator } from "./typingIndicator";
import { useCopied } from "@/shared/hooks/useCopy";
import { Image } from "@/shared/ui/image/image";
import { useParams } from "react-router-dom";
import { FileMessage } from "./fileMessage";
import { TAG_COLORS } from "../tagSelector/tagSelector";
import { useState } from "react";
import { useTelegramStatusQuery } from "@/entities/auth/hooks/useTelegramStatus";
import { useTodoistStatusQuery } from "@/entities/auth/hooks/useTodoistStatus";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import { sendTelegramMessage } from "@/entities/auth/api/authService";
import { TelegramContact } from "@/entities/auth/types/types";
import { useGraphLogsContext } from "../chat/chat";
import { useGraphLogsQuery } from "@/entities/chat/hooks/useGraphLogs";
import { SourcesButton } from "./sourcesButton";
import { VoiceMessage } from "./voiceMessage";

export interface MessageProps {
  id: string;
  content: string;
  isUser: boolean;
  answerId?: number;
  rating?: number | null;
  isTyping?: boolean;
  question_file_url?: string;
  answer_file_url?: string;
  voice_url?: string;
  isCompact?: boolean;
  tag: string;
}

export const Message = ({
  id,
  content,
  isUser,
  answerId,
  tag,
  rating,
  isTyping = false,
  question_file_url,
  answer_file_url,
  voice_url,
  isCompact = false,
}: MessageProps) => {
  const chatId = useParams().chatId;

  const { openModal } = useModal();

  const { handleCopyClick, isCopied } = useCopied();

  const [isSendingTelegram, setIsSendingTelegram] = useState(false);

  const graphLogsContext = useGraphLogsContext();

  const shouldCheckLogs = !!answerId && !!graphLogsContext;
  const { data: graphLogs } = useGraphLogsQuery(
    shouldCheckLogs ? answerId : undefined
  );

  const hasGraphLogs = graphLogs && graphLogs.length > 0;

  const getStoredPhoneNumber = (): string | undefined => {
    try {
      const stored = localStorage.getItem("telegram_phone_number");
      return stored || undefined;
    } catch {
      return undefined;
    }
  };

  const phone_number = getStoredPhoneNumber();
  const { data: telegramStatus } = useTelegramStatusQuery(phone_number);

  const { data: profileData } = useGetProfileQuery();
  const user_id = profileData?.id?.toString();
  const { data: todoistStatus } = useTodoistStatusQuery(user_id);

  const handleSendToTelegram = () => {
    if (!phone_number || !telegramStatus?.authorized) {
      console.warn("Telegram not authorized. Please authorize first.");
      return;
    }

    const tg_user_id = telegramStatus?.user_info?.id;
    const request_data = tg_user_id
      ? { tg_user_id }
      : phone_number
      ? { phone_number }
      : null;

    if (!request_data) {
      console.warn("No phone_number or tg_user_id available");
      return;
    }

    openModal(EModalVariables.TELEGRAM_CONTACTS_MODAL, {
      ...request_data,
      message_text: content,
      onSelect: async (contact: TelegramContact, truncatedText?: string) => {
        if (!phone_number || !content.trim()) {
          return;
        }

        const textToSend = truncatedText || content;

        setIsSendingTelegram(true);
        try {
          await sendTelegramMessage({
            phone_number,
            recipient_id: contact.id,
            text: textToSend,
          });
        } catch (error) {
          console.error("Failed to send Telegram message:", error);
        } finally {
          setIsSendingTelegram(false);
        }
      },
    });
  };

  const handleLikeClick = () => {
    if (answerId) {
      openModal(EModalVariables.RATING_MODAL, {
        answerId,
        chatId: Number(chatId),
      });
    }
  };

  const handleCreateTodoistTask = () => {
    if (!user_id || !content.trim()) {
      console.warn("No user_id or content available");
      return;
    }

    openModal(EModalVariables.TODOIST_CREATE_TASK_MODAL, {
      user_id,
      content: content.trim(),
      labels: tag ? [tag] : undefined,
    });
  };

  return (
    <div
      data-message-id={id}
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
        {isUser && (
          <>
            {question_file_url && <FileMessage fileUrl={question_file_url} />}
            {voice_url && voice_url.trim() && (
              <div className="mb-2">
                <VoiceMessage voiceUrl={voice_url} transcription={content} />
              </div>
            )}
            {question_file_url && content && content.trim() && !voice_url && (
              <div
                className={cn(
                  "rounded-2xl px-4 py-3 text-sm md:text-base leading-relaxed mt-2",
                  "bg-red-50 dark:bg-red-500/20 text-foreground rounded-tr-sm border border-red-100 dark:border-red-500/30"
                )}
              >
                {content}
              </div>
            )}
            {!question_file_url && !voice_url && content && content.trim() && (
              <div
                className={cn(
                  "rounded-2xl text-sm md:text-base leading-relaxed",
                  "break-words overflow-wrap-anywhere w-full",
                  "px-4 py-3 bg-red-50 dark:bg-red-500/20 text-foreground rounded-tr-sm border border-red-100 dark:border-red-500/30",
                  isCompact && "text-sm md:text-sm"
                )}
              >
                {content}
              </div>
            )}
          </>
        )}

        {!isUser && (
          <>
            {answer_file_url && <FileMessage fileUrl={answer_file_url} />}
            {answer_file_url && content && content.trim() && (
              <div
                className={cn(
                  "rounded-2xl py-0 text-sm md:text-base leading-relaxed mt-2",
                  "text-foreground rounded-xl dark:border-gray-700"
                )}
              >
                <MarkdownContent content={content} />
              </div>
            )}
            {!answer_file_url && (
              <div
                className={cn(
                  "rounded-2xl text-sm md:text-base leading-relaxed",
                  "break-words overflow-wrap-anywhere w-full",
                  "text-foreground rounded-xl dark:border-gray-700",
                  isCompact && "text-sm md:text-sm"
                )}
              >
                {isTyping ? (
                  <TypingIndicator />
                ) : (
                  <MarkdownContent content={content} />
                )}
              </div>
            )}
          </>
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
            {telegramStatus?.authorized && (
              <button
                disabled={isSendingTelegram || !content.trim()}
                className={cn(
                  "p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer",
                  (isSendingTelegram || !content.trim()) &&
                    "opacity-50 cursor-not-allowed"
                )}
                aria-label="Отправить в Telegram"
                onClick={handleSendToTelegram}
                title="Отправить в Telegram"
              >
                <Send className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </button>
            )}
            {todoistStatus?.authorized && (
              <button
                disabled={!content.trim()}
                className={cn(
                  "p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer",
                  !content.trim() && "opacity-50 cursor-not-allowed"
                )}
                aria-label="Создать задачу в Todoist"
                onClick={handleCreateTodoistTask}
                title="Создать задачу в Todoist"
              >
                <CheckSquare className="h-4 w-4 text-purple-600 dark:text-purple-400" />
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
            {!isCompact &&
              answerId &&
              graphLogsContext &&
              hasGraphLogs &&
              graphLogs && (
                <SourcesButton
                  count={graphLogs.length}
                  onClick={() => graphLogsContext?.openGraphLogs(answerId)}
                />
              )}
          </div>
        )}
      </div>
    </div>
  );
};
