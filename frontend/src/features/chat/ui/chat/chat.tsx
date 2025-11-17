import {
  memo,
  useRef,
  useCallback,
  useState,
  createContext,
  useContext,
  useEffect,
} from "react";
import { ChatHeader } from "../chatHeader";
import { MessageList } from "../messageList";
import { ChatInput } from "../chatInput";
import { type Suggestion } from "../suggestions";
import type { MessageData } from "@/shared/types/message";
import { MessageLadder } from "../message/messageLadder";
import { GraphLogsViewer } from "../graphLogsViewer";

interface GraphLogsContextType {
  openGraphLogs: (answerId: number) => void;
  closeGraphLogs: () => void;
  currentAnswerId: number | null;
  isGraphLogsOpen: boolean;
}

const GraphLogsContext = createContext<GraphLogsContextType | null>(null);

export const useGraphLogsContext = () => {
  return useContext(GraphLogsContext);
};

export interface ChatProps {
  messages?: MessageData[];
  onSendMessage?: (data: { message: string; file_url?: string }) => void;
  onSendVoice?: (voiceBlob: Blob) => void;
  isLoading?: boolean;
  suggestions?: Suggestion[];
  hideHeader?: boolean;
  isCompact?: boolean;
}

export const Chat = memo(
  ({
    messages = [],
    onSendMessage,
    onSendVoice,
    isLoading = false,
    suggestions,
    hideHeader = false,
    isCompact = false,
  }: ChatProps) => {
    const scrollContainerRef = useRef<HTMLElement | null>(null);
    const scrollButtonContainerRef = useRef<HTMLDivElement>(null);
    const [isGraphLogsOpen, setIsGraphLogsOpen] = useState(false);
    const [currentAnswerId, setCurrentAnswerId] = useState<number | null>(null);

    const prevIsLoadingRef = useRef<boolean>(false);
    const lastProcessedAnswerIdRef = useRef<number | null>(null);

    const handleScrollContainerReady = useCallback(
      (ref: React.RefObject<HTMLElement>) => {
        if (ref.current) {
          scrollContainerRef.current = ref.current;
        }
      },
      []
    );

    const openGraphLogs = useCallback((answerId: number) => {
      setCurrentAnswerId(answerId);
      setIsGraphLogsOpen(true);
    }, []);

    const closeGraphLogs = useCallback(() => {
      setIsGraphLogsOpen(false);
      setCurrentAnswerId(null);
    }, []);

    useEffect(() => {
      const lastBotMessage = [...messages]
        .reverse()
        .find((msg) => !msg.isUser && msg.answerId);

      if (
        !lastBotMessage ||
        lastBotMessage.isUser ||
        !lastBotMessage.answerId
      ) {
        prevIsLoadingRef.current = isLoading;
        return;
      }

      const newAnswerId = lastBotMessage.answerId;
      const isGenerationStarted = !prevIsLoadingRef.current && isLoading;
      const isNewAnswerId = newAnswerId !== lastProcessedAnswerIdRef.current;

      if (isLoading && (isGenerationStarted || isNewAnswerId)) {
        setCurrentAnswerId(newAnswerId);
        if (!isGraphLogsOpen || isGenerationStarted) {
          setIsGraphLogsOpen(true);
        }
        lastProcessedAnswerIdRef.current = newAnswerId;
      }

      prevIsLoadingRef.current = isLoading;
    }, [isLoading, messages, isGraphLogsOpen]);

    return (
      <GraphLogsContext.Provider
        value={{
          openGraphLogs,
          closeGraphLogs,
          currentAnswerId,
          isGraphLogsOpen,
        }}
      >
        <div className="flex h-full flex-col bg-white overflow-hidden relative">
          <div className="flex-1 flex overflow-hidden relative">
            <div className="flex-1 flex flex-col min-w-0">
              {!hideHeader && <ChatHeader />}
              <div className="flex-1 overflow-hidden flex justify-center relative">
                <MessageList
                  messages={messages}
                  isLoading={isLoading}
                  isCompact={isCompact}
                  onScrollContainerReady={handleScrollContainerReady}
                  scrollButtonContainerRef={scrollButtonContainerRef}
                />
                {!isCompact && (
                  <MessageLadder
                    messages={messages}
                    scrollContainerRef={scrollContainerRef}
                  />
                )}
              </div>
              <ChatInput
                ref={scrollButtonContainerRef}
                onSend={onSendMessage}
                onSendVoice={onSendVoice}
                disabled={isLoading}
                suggestions={suggestions}
                isCompact={isCompact}
              />
            </div>
            <GraphLogsViewer
              answerId={currentAnswerId || 0}
              isOpen={isGraphLogsOpen && !!currentAnswerId}
              onClose={closeGraphLogs}
            />
          </div>
        </div>
      </GraphLogsContext.Provider>
    );
  }
);

Chat.displayName = "Chat";
