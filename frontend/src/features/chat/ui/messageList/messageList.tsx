import { ScrollArea } from "@/shared/ui/scroll-area";
import { Message } from "../message";

export interface MessageData {
  id: string;
  content: string;
  isUser: boolean;
  timestamp?: string;
}

export interface MessageListProps {
  messages: MessageData[];
}

export const MessageList = ({ messages }: MessageListProps) => {
  return (
    <ScrollArea className="flex-1 max-w-[832px]">
      <div>
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center px-4 md:px-8 py-12">
            <div className="text-center space-y-4 max-w-md">
              <div className="mx-auto flex h-16 w-16 md:h-20 md:w-20 items-center justify-center rounded-full bg-red-500/10 backdrop-blur-md">
                <svg
                  className="h-8 w-8 md:h-10 md:w-10 text-red-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-xl md:text-2xl font-semibold text-foreground mb-2">
                  Как я могу вам помочь?
                </h3>
                <p className="text-sm text-muted-foreground">
                  Начните новый разговор, задав вопрос ниже
                </p>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <Message
              key={message.id}
              content={message.content}
              isUser={message.isUser}
            />
          ))
        )}
      </div>
    </ScrollArea>
  );
};
