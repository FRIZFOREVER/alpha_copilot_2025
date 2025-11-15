import { useState, useRef, useEffect } from "react";
import { Button } from "@/shared/ui/button";
import { Mic, ChevronUp, X, Check, Paperclip, Send } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { useComputerVoiceRecorder } from "@/entities/chat/hooks/useComputerVoiceRecorder";
import { formatTime } from "@/shared/lib/utils/timeHelpers";
import { Suggestions, type Suggestion } from "../suggestions";
import { useFileAttachments } from "../../hooks/useFileAttachments";
import { FileBadge } from "../fileBadge";
import { uploadFile } from "@/entities/chat/api/chatService";
import { TagSelector, type TagId } from "../tagSelector/tagSelector";
import { TagBadge } from "../tagBadge/tagBadge";
import { TelegramContact } from "@/entities/auth/types/types";

export interface ChatInputProps {
  onSend?: (data: { message: string; file_url?: string; tag?: TagId }) => void;
  onSendVoice?: (voiceBlob: Blob) => void;
  placeholder?: string;
  disabled?: boolean;
  suggestions?: Suggestion[];
  isCompact?: boolean;
  selectedTelegramContact?: TelegramContact | null;
  onTelegramContactClick?: () => void;
}

const MIN_HEIGHT = 52;

export const ChatInput = ({
  onSend,
  onSendVoice,
  placeholder = "Спросите что-нибудь...",
  disabled = false,
  suggestions,
  isCompact = false,
  selectedTelegramContact,
  onTelegramContactClick,
}: ChatInputProps) => {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isMultiLine, setIsMultiLine] = useState(false);
  const [needsScrollbar, setNeedsScrollbar] = useState(false);
  const recordedBlobRef = useRef<Blob | null>(null);
  const shouldSendBlobRef = useRef(false);
  const [selectedTag, setSelectedTag] = useState<TagId | undefined>(undefined);
  const [showTagSelector, setShowTagSelector] = useState(false);
  const [tagSelectorPosition, setTagSelectorPosition] = useState<{
    top?: number;
    bottom?: number;
    left: number;
  }>({ bottom: 0, left: 0 });
  const [shouldShowTagSelector, setShouldShowTagSelector] = useState(false);
  const tagSelectorRef = useRef<HTMLDivElement>(null);

  const { file, addFile, removeFile, clearFile, selectFile, hasFile } =
    useFileAttachments();

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

  const handleSend = async () => {
    if (message.trim() && !disabled) {
      let fileUrl: string | undefined;

      if (file) {
        try {
          const uploadResult = await uploadFile(file.file);
          fileUrl = uploadResult?.file_url;
        } catch (error) {
          console.error("Ошибка при загрузке файла:", error);
        }
      }

      let finalTag: TagId | undefined = selectedTag;
      if (!finalTag) {
        const tagMatch = message.match(
          /#(general|finance|law|marketing|managment)\b/,
        );
        if (tagMatch) {
          finalTag = tagMatch[1] as TagId;
        }
      }

      onSend?.({
        message: message.trim(),
        file_url: fileUrl,
        tag: selectedTag || finalTag,
      });
      setMessage("");
      setSelectedTag(undefined);
      clearFile();
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
      setShowTagSelector(false);
      handleSend();
    } else if (e.key === "Escape") {
      setShowTagSelector(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setMessage(value);

    const cursorPosition = e.target.selectionStart;
    const textBeforeCursor = value.substring(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf("@");

    if (lastAtIndex !== -1) {
      const textAfterAt = textBeforeCursor.substring(lastAtIndex + 1);
      if (textAfterAt.length === 0 || /^[a-zA-Z]*$/.test(textAfterAt)) {
        setShouldShowTagSelector(true);
      } else {
        setShouldShowTagSelector(false);
        setShowTagSelector(false);
      }
    } else {
      setShouldShowTagSelector(false);
      setShowTagSelector(false);
    }
  };

  const handleSuggestionSelect = (suggestion: Suggestion) => {
    const fullText = `${suggestion.title} ${suggestion.subtitle}`;
    setMessage(fullText);
    textareaRef.current?.focus();
  };

  const handleTagSelect = (tag: TagId) => {
    const cursorPosition = textareaRef.current?.selectionStart || 0;
    const textBeforeCursor = message.substring(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf("@");

    if (lastAtIndex !== -1) {
      const textAfterCursor = message.substring(cursorPosition);
      const newMessage = message.substring(0, lastAtIndex) + textAfterCursor;

      setMessage(newMessage);
      setSelectedTag(tag);
      setShowTagSelector(false);
      setShouldShowTagSelector(false);

      setTimeout(() => {
        if (textareaRef.current) {
          const newCursorPosition = lastAtIndex;
          textareaRef.current.setSelectionRange(
            newCursorPosition,
            newCursorPosition,
          );
          textareaRef.current.focus();
        }
      }, 0);
    }
  };

  const handleTagRemove = () => {
    setSelectedTag(undefined);
  };

  const handleTagSelectorClose = () => {
    setShowTagSelector(false);
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

  const handleFileSelect = async () => {
    if (disabled) return;

    const selectedFile = await selectFile();
    if (selectedFile) {
      addFile(selectedFile);
    }
  };

  useEffect(() => {
    requestAnimationFrame(() => {
      updateTextareaHeight();
    });
  }, [message, file]);

  useEffect(() => {
    if (
      shouldShowTagSelector &&
      textareaRef.current &&
      tagSelectorRef.current
    ) {
      requestAnimationFrame(() => {
        if (textareaRef.current && tagSelectorRef.current) {
          const textareaRect = textareaRef.current.getBoundingClientRect();
          const containerRect = tagSelectorRef.current.getBoundingClientRect();

          if (containerRect && textareaRect) {
            const left = textareaRect.left - containerRect.left;
            let bottom = containerRect.bottom - textareaRect.top + 8;

            if(file && !selectedTag) {
              bottom += 75;
            }

            if(selectedTag && !file) {
              bottom += 45;
            }

            if(selectedTag && file) {
              bottom += 110;
            }

            setTagSelectorPosition({ bottom, left });
            setShowTagSelector(true);
          }
        }
      });
    } else if (!shouldShowTagSelector) {
      setShowTagSelector(false);
    }
  }, [shouldShowTagSelector]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        tagSelectorRef.current &&
        !tagSelectorRef.current.contains(event.target as Node) &&
        !textareaRef.current?.contains(event.target as Node)
      ) {
        setShowTagSelector(false);
        setShouldShowTagSelector(false);
      }
    };

    if (showTagSelector) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [showTagSelector]);

  return (
    <div className="bg-white">
      <div
        className={cn(
          "mx-auto max-w-[832px] px-4 md:px-8 py-4",
          isCompact && "px-4 md:px-4",
        )}
      >
        {suggestions && suggestions.length > 0 && (
          <Suggestions
            suggestions={suggestions}
            onSelect={handleSuggestionSelect}
            isCompact={isCompact}
            className="mb-2"
          />
        )}
        <div className="relative overflow-visible" ref={tagSelectorRef}>
          {showTagSelector && (
            <TagSelector
              onSelect={handleTagSelect}
              onClose={handleTagSelectorClose}
              position={tagSelectorPosition}
            />
          )}
          {isRecording ? (
            <div className="w-full min-h-[50px] rounded-[24px] shadow-sm mb-[13px] px-12 py-3 pr-20 bg-white border border-gray-200 flex items-center relative">
              <button
                type="button"
                className="absolute left-3 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={disabled}
                onClick={handleFileSelect}
              >
                <Paperclip className="h-5 w-5" />
              </button>

              <div className="flex-1 flex items-center px-2">
                <div className="flex-1 border-b-2 border-dotted border-gray-400"></div>
                <span className="ml-3 text-sm text-gray-500">
                  {formatTime(elapsedSec)}
                </span>
              </div>

              <button
                type="button"
                className={cn(
                  "absolute right-12 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200",
                )}
                disabled={disabled}
                onClick={handleCancelRecording}
              >
                <X className="h-5 w-5" />
              </button>

              <button
                type="button"
                disabled={disabled}
                className={cn(
                  "absolute right-2 h-8 w-8 rounded-full cursor-pointer",
                  "bg-black hover:bg-gray-800",
                  "text-white transition-all shadow-sm duration-200",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  "active:scale-95 flex items-center justify-center",
                )}
                onClick={handleSendVoice}
              >
                <Check className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div
              className={cn(
                "w-full min-h-[50px] rounded-[24px] shadow-sm",
                "bg-white border border-gray-200",
                "focus-within:border-gray-300",
                "transition-all",
                "relative",
                "flex flex-col",
              )}
            >
              {(hasFile || selectedTag || selectedTelegramContact) && (
                <div className="px-3 pt-3 pb-2 flex flex-col gap-2">
                  {selectedTag && (
                    <div className="flex items-center">
                      <TagBadge
                        tagId={selectedTag}
                        onRemove={handleTagRemove}
                        disabled={disabled}
                      />
                    </div>
                  )}
                  {hasFile && file && (
                    <div className="flex items-center">
                      <FileBadge
                        file={file}
                        onRemove={removeFile}
                        disabled={disabled}
                      />
                    </div>
                  )}
                  {selectedTelegramContact && (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-200">
                      <Send className="h-4 w-4 text-blue-600" />
                      <span className="text-sm text-blue-900 font-medium">
                        {selectedTelegramContact.first_name}{" "}
                        {selectedTelegramContact.last_name}
                      </span>
                      {selectedTelegramContact.username && (
                        <span className="text-xs text-blue-600">
                          @{selectedTelegramContact.username}
                        </span>
                      )}
                      {onTelegramContactClick && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            onTelegramContactClick();
                          }}
                          className="ml-auto text-blue-600 hover:text-blue-800"
                          disabled={disabled}
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}
              <div className="relative flex-1 flex items-stretch">
                <textarea
                  ref={textareaRef}
                  value={message}
                  placeholder={placeholder}
                  disabled={disabled}
                  rows={1}
                  className={cn(
                    "w-full min-h-[50px] max-h-[200px] resize-none",
                    "px-12 py-3.5 md:py-3 pr-20",
                    "bg-transparent",
                    "text-sm md:text-base text-gray-900 placeholder:text-gray-400",
                    "focus:outline-none",
                    "transition-all",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    needsScrollbar && "overflow-y-auto custom-scrollbar",
                    !needsScrollbar && "overflow-hidden",
                  )}
                  style={{
                    height: "auto",
                  }}
                  onChange={handleChange}
                  onKeyDown={handleKeyDown}
                />
                <button
                  type="button"
                  className={cn(
                    "absolute left-3 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                    isMultiLine ? "bottom-3" : "top-[50%] -translate-y-1/2",
                  )}
                  disabled={disabled}
                  onClick={handleFileSelect}
                >
                  <Paperclip className="h-5 w-5" />
                </button>

                {onTelegramContactClick && (
                  <button
                    type="button"
                    className={cn(
                      "absolute left-12 h-6 w-6 flex items-center cursor-pointer justify-center transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                      isMultiLine ? "bottom-3" : "top-[50%] -translate-y-1/2",
                      selectedTelegramContact
                        ? "text-blue-600 hover:text-blue-800"
                        : "text-gray-700 hover:text-gray-900",
                    )}
                    disabled={disabled}
                    onClick={onTelegramContactClick}
                    title={
                      selectedTelegramContact
                        ? "Изменить контакт Telegram"
                        : "Выбрать контакт Telegram"
                    }
                  >
                    <Send className="h-5 w-5" />
                  </button>
                )}

                <button
                  type="button"
                  className={cn(
                    "absolute right-12 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                    isMultiLine ? "bottom-3" : "top-[50%] -translate-y-1/2",
                    isRecording && "text-red-500",
                  )}
                  disabled={disabled}
                  onClick={handleMicClick}
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
                    isMultiLine ? "bottom-2" : "top-[50%] -translate-y-1/2",
                  )}
                  size="icon"
                >
                  <ChevronUp className="h-4 w-4" />
                </Button>
              </div>
            </div>
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
