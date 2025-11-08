import { Bot, User } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";

export interface MessageProps {
  content: string;
  isUser: boolean;
  timestamp?: string;
}

export const Message = ({ content, isUser, timestamp }: MessageProps) => {
  return (
    <div
      className={cn(
        "flex gap-4 px-4 md:px-8 py-4 md:py-6",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
          <Bot className="h-5 w-5 text-muted-foreground" />
        </div>
      )}
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
              : "bg-zinc-100 text-foreground rounded-tl-sm"
          )}
        >
          {content}
        </div>
      </div>
      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-50 dark:bg-red-500/20 border border-red-100 dark:border-red-500/30">
          <User className="h-5 w-5 text-red-500" />
        </div>
      )}
    </div>
  );
};
