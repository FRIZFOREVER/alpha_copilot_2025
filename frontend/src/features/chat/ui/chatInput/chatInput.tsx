import { useState, useRef, useEffect } from "react";
import { Button } from "@/shared/ui/button";
import { Plus, Mic, ChevronUp } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";

export interface ChatInputProps {
  onSend?: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

const MIN_HEIGHT = 52;

export const ChatInput = ({
  onSend,
  placeholder = "Спросите что-нибудь...",
  disabled = false,
}: ChatInputProps) => {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isMultiLine, setIsMultiLine] = useState(false);
  const [needsScrollbar, setNeedsScrollbar] = useState(false);

  const updateTextareaHeight = () => {
    if (!textareaRef.current) return;

    const target = textareaRef.current;
    target.style.height = "auto";
    const scrollHeight = target.scrollHeight;
    const newHeight = Math.min(scrollHeight, 200);
    target.style.height = `${newHeight}px`;

    setIsMultiLine(scrollHeight > MIN_HEIGHT);

    setNeedsScrollbar(scrollHeight > 200);
  };

  useEffect(() => {
    requestAnimationFrame(() => {
      updateTextareaHeight();
    });
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend?.(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
        setIsMultiLine(false);
        setNeedsScrollbar(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
  };

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-[832px] px-4 md:px-8 py-4 md:pt-6">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={cn(
              "w-full min-h-[52px] max-h-[200px] resize-none",
              "px-12 py-3 pr-20 rounded-[24px]",
              "bg-white border border-gray-200",
              "text-sm md:text-base text-gray-900 placeholder:text-gray-400",
              "focus:outline-none focus:border-gray-300",
              "transition-all shadow-sm",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              needsScrollbar && "overflow-y-auto custom-scrollbar",
              !needsScrollbar && "overflow-hidden"
            )}
            style={{
              height: "auto",
            }}
          />
          <button
            type="button"
            className={cn(
              "absolute left-3 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
              isMultiLine ? "bottom-5" : "top-[45%] -translate-y-1/2"
            )}
            disabled={disabled}
          >
            <Plus className="h-5 w-5" />
          </button>

          <button
            type="button"
            className={cn(
              "absolute right-12 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
              isMultiLine ? "bottom-5" : "top-[45%] -translate-y-1/2"
            )}
            disabled={disabled}
          >
            <Mic className="h-5 w-5" />
          </button>

          <Button
            onClick={handleSend}
            disabled={!message.trim() || disabled}
            className={cn(
              "absolute right-2 h-8 w-8 rounded-full cursor-pointer",
              "bg-black hover:bg-gray-800",
              "text-white transition-all shadow-sm duration-200",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "active:scale-95 p-0",
              isMultiLine ? "bottom-4" : "top-[45%] -translate-y-1/2"
            )}
            size="icon"
          >
            <ChevronUp className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-center text-muted-foreground mt-3">
          AI Copilot может допускать ошибки. Проверьте важную информацию.
        </p>
      </div>
    </div>
  );
};
