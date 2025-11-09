import { useState, useRef, useEffect } from "react";
import { Button } from "@/shared/ui/button";
import { Plus, Mic, ChevronUp, X, Check } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { useComputerVoiceRecorder } from "@/entities/chat/hooks/useComputerVoiceRecorder";

export interface ChatInputProps {
  onSend?: (message: string) => void;
  onSendVoice?: (voiceBlob: Blob) => void;
  placeholder?: string;
  disabled?: boolean;
}

const MIN_HEIGHT = 52;

export const ChatInput = ({
  onSend,
  onSendVoice,
  placeholder = "Спросите что-нибудь...",
  disabled = false,
}: ChatInputProps) => {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isMultiLine, setIsMultiLine] = useState(false);
  const [needsScrollbar, setNeedsScrollbar] = useState(false);
  const recordedBlobRef = useRef<Blob | null>(null);
  const shouldSendBlobRef = useRef(false);

  const { isRecording, elapsedSec, error, startRecording, stopRecording } =
    useComputerVoiceRecorder({
      sendCallback: (blob: Blob) => {
        recordedBlobRef.current = blob;
        if (shouldSendBlobRef.current && onSendVoice) {
          onSendVoice(blob);
          recordedBlobRef.current = null;
          shouldSendBlobRef.current = false;
        }
      },
    });

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

  const handleMicClick = async () => {
    if (isRecording) {
      shouldSendBlobRef.current = false;
      stopRecording();
      recordedBlobRef.current = null;
    } else {
      try {
        await startRecording();
      } catch (err) {
        console.error("Failed to start recording:", err);
      }
    }
  };

  const handleCancelRecording = () => {
    shouldSendBlobRef.current = false;
    stopRecording();
    recordedBlobRef.current = null;
  };

  const handleSendVoice = () => {
    if (isRecording) {
      shouldSendBlobRef.current = true;
      stopRecording();
    } else if (recordedBlobRef.current && onSendVoice) {
      onSendVoice(recordedBlobRef.current);
      recordedBlobRef.current = null;
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-[832px] px-4 md:px-8 py-4 md:pt-6">
        <div className="relative">
          {isRecording ? (
            <div
              className={cn(
                "w-full min-h-[52px] rounded-[24px]",
                "px-12 py-3 pr-20",
                "bg-white border border-gray-200",
                "flex items-center",
                "relative"
              )}
            >
              <button
                type="button"
                className={cn(
                  "absolute left-3 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200"
                )}
                disabled={disabled}
              >
                <Plus className="h-5 w-5" />
              </button>

              <div className="flex-1 flex items-center px-2">
                <div className="flex-1 border-b-2 border-dotted border-gray-400"></div>
                <span className="ml-3 text-sm text-gray-500">
                  {formatTime(elapsedSec)}
                </span>
              </div>

              <button
                type="button"
                onClick={handleCancelRecording}
                className={cn(
                  "absolute right-12 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200"
                )}
                disabled={disabled}
              >
                <X className="h-5 w-5" />
              </button>

              <button
                type="button"
                onClick={handleSendVoice}
                disabled={disabled}
                className={cn(
                  "absolute right-2 h-8 w-8 rounded-full cursor-pointer",
                  "bg-black hover:bg-gray-800",
                  "text-white transition-all shadow-sm duration-200",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  "active:scale-95 flex items-center justify-center"
                )}
              >
                <Check className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <>
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
                  "px-12 py-3.5 md:py-3 pr-20 rounded-[24px]",
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
                onClick={handleMicClick}
                className={cn(
                  "absolute right-12 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                  isMultiLine ? "bottom-5" : "top-[45%] -translate-y-1/2",
                  isRecording && "text-red-500"
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
            </>
          )}
          {error && <p className="text-xs text-red-500 mt-2 px-4">{error}</p>}
        </div>
        <p className="text-xs text-center text-muted-foreground mt-3">
          AI Copilot может допускать ошибки. Проверьте важную информацию.
        </p>
      </div>
    </div>
  );
};
