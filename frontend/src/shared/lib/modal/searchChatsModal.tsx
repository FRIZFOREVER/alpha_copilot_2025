import { Dialog, DialogContent } from "@/shared/ui/dialog/dialog";
import { useModal } from "./context";
import { useState, useEffect, useCallback } from "react";
import { MessageSquare } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { EModalVariables } from "./constants";
import { DialogTitle } from "@radix-ui/react-dialog";
import { debounce } from "lodash";
import { searchMessages } from "@/entities/chat/api/chatService";
import { SearchMessageResult } from "@/entities/chat/types/types";

export const SearchChatsModal = () => {
  const { isOpen, selectType, closeModal } = useModal();
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<SearchMessageResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isSearchModal = selectType === EModalVariables.SEARCH_CHATS_MODAL;

  const performSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await searchMessages(query);
      setResults(data ?? []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Ошибка при поиске сообщений",
      );
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const debouncedSearch = useCallback(
    debounce((query: string) => {
      performSearch(query);
    }, 500),
    [performSearch],
  );

  useEffect(() => {
    if (isOpen && isSearchModal) {
      setSearchQuery("");
      setResults([]);
      setError(null);
      setIsLoading(false);
    }
  }, [isOpen, isSearchModal]);

  useEffect(() => {
    debouncedSearch(searchQuery);
    return () => {
      debouncedSearch.cancel();
    };
  }, [searchQuery, debouncedSearch]);

  const handleClose = () => {
    closeModal();
    setSearchQuery("");
    setResults([]);
    setError(null);
    setIsLoading(false);
  };

  const highlightQuery = (text: string, query: string) => {
    if (!query) return text;
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const parts = text.split(new RegExp(`(${escapedQuery})`, "gi"));
    return parts.map((part, index) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <strong key={index} className="font-semibold">
          {part}
        </strong>
      ) : (
        part
      ),
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (!isSearchModal) return null;

  return (
    <Dialog open={isOpen && isSearchModal} onOpenChange={handleClose}>
      <DialogContent
        className={cn(
          "md:max-w-[600px] md:w-[calc(100%-2rem)]",
          "md:rounded-3xl md:h-[460px] md:max-h-[80vh]",
          "w-full h-full max-w-none max-h-none",
          "rounded-none md:rounded-3xl",
          "m-0 md:m-4",
          "top-0 left-0 right-0 bottom-0",
          "translate-x-0 translate-y-0",
          "md:translate-x-[-50%] md:translate-y-[-50%]",
          "md:top-[50%] md:left-[50%]",
          "bg-white p-0",
          "border-0 shadow-lg",
          "overflow-hidden",
        )}
        showCloseButton={true}
      >
        <DialogTitle className="hidden">Поиск в чатах</DialogTitle>
        <div
          className={cn("flex flex-col", "h-full md:h-[460px] md:max-h-[80vh]")}
        >
          <div className="px-6 pt-6 pb-4 border-b border-gray-100">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Поиск в чатах..."
              className={cn(
                "w-full text-base text-gray-900 placeholder:text-gray-400",
                "bg-transparent border-0 outline-none",
                "focus:ring-0 focus:outline-none",
                "font-normal",
              )}
              autoFocus
            />
          </div>

          <div className="flex-1 overflow-y-auto px-2 py-2">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center h-full text-center px-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400 mb-3"></div>
                <p className="text-sm text-gray-400">Поиск...</p>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center h-full text-center px-4">
                <MessageSquare className="h-12 w-12 text-gray-300 mb-3" />
                <p className="text-sm text-red-500 mb-1">Ошибка</p>
                <p className="text-xs text-gray-400">{error}</p>
              </div>
            ) : results.length > 0 ? (
              <div className="space-y-0">
                {results.map((result) => (
                  <button
                    key={`${result.question_id}-${result.answer_id}`}
                    className={cn(
                      "w-full text-left px-4 py-3 rounded-lg",
                      "hover:bg-gray-50 active:bg-gray-100 transition-colors",
                      "flex items-start gap-3",
                      "cursor-pointer",
                      "border-0 outline-none focus:outline-none",
                    )}
                    onClick={() => {
                      handleClose();
                    }}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <MessageSquare className="h-5 w-5 text-gray-400 stroke-[1.5]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-gray-900 mb-1 leading-tight">
                        {highlightQuery(result.question, searchQuery)}
                      </div>
                      <div className="text-xs text-gray-500 line-clamp-2 leading-relaxed mb-1">
                        {highlightQuery(result.answer, searchQuery)}
                      </div>
                      <div className="text-xs text-gray-400">
                        {formatDate(result.question_time)}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center px-4">
                <MessageSquare className="h-12 w-12 text-gray-300 mb-3" />
                <p className="text-sm text-gray-400">
                  {searchQuery
                    ? "Ничего не найдено"
                    : "Начните вводить запрос для поиска"}
                </p>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
