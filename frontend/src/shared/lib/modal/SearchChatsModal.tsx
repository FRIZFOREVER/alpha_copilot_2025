import { Dialog, DialogContent } from "@/shared/ui/dialog/dialog";
import { useModal } from "./context";
import { useState, useEffect } from "react";
import { MessageSquare } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { EModalVariables } from "./constants";

interface SearchResult {
  id: string;
  title: string;
  snippet: string;
  chatId: string;
  chatName: string;
}

export const SearchChatsModal = () => {
  const { isOpen, selectType, closeModal } = useModal();
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);

  const isSearchModal = selectType === EModalVariables.SEARCH_CHATS_MODAL;

  useEffect(() => {
    if (isOpen && isSearchModal) {
      setSearchQuery("");
      setResults([
        {
          id: "1",
          title: "Стилизация блока приветствия",
          snippet: "...привет в docs файле...",
          chatId: "1",
          chatName: "Дизайн",
        },
        {
          id: "2",
          title: "Привет в docs файле",
          snippet: "...привет в документации...",
          chatId: "2",
          chatName: "Документация",
        },
        {
          id: "3",
          title: "Решение синуса выражения",
          snippet: "...математическое выражение...",
          chatId: "3",
          chatName: "Математика",
        },
        {
          id: "4",
          title: "Отформатировать схему Prisma",
          snippet: "...🚀 Привет! Нужно отформатировать...",
          chatId: "4",
          chatName: "Backend",
        },
        {
          id: "5",
          title: "npm install error",
          snippet: "...🚀 Привет! Ошибка при установке...",
          chatId: "5",
          chatName: "Frontend",
        },
        {
          id: "6",
          title: "Enum форматы дат",
          snippet: "...форматы дат в enum...",
          chatId: "6",
          chatName: "Разработка",
        },
        {
          id: "7",
          title: "Enum форматы дат",
          snippet: "...форматы дат в enum...",
          chatId: "6",
          chatName: "Разработка",
        },
        {
          id: "8",
          title: "Enum форматы дат",
          snippet: "...форматы дат в enum...",
          chatId: "6",
          chatName: "Разработка",
        },
        {
          id: "9",
          title: "Enum форматы дат",
          snippet: "...форматы дат в enum...",
          chatId: "6",
          chatName: "Разработка",
        },
      ]);
    }
  }, [isOpen, isSearchModal]);

  const filteredResults = results.filter((result) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      result.title.toLowerCase().includes(query) ||
      result.snippet.toLowerCase().includes(query)
    );
  });

  const handleClose = () => {
    closeModal();
    setSearchQuery("");
    setResults([]);
  };

  const highlightQuery = (text: string, query: string) => {
    if (!query) return text;
    const parts = text.split(new RegExp(`(${query})`, "gi"));
    return parts.map((part, index) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <strong key={index} className="font-semibold">
          {part}
        </strong>
      ) : (
        part
      )
    );
  };

  if (!isSearchModal) return null;

  return (
    <Dialog open={isOpen && isSearchModal} onOpenChange={handleClose}>
      <DialogContent
        className={cn(
          "max-w-[600px] w-[calc(100%-2rem)]",
          "bg-white rounded-3xl p-0",
          "border-0 shadow-lg",
          "overflow-hidden"
        )}
        showCloseButton={true}
      >
        <div className="flex flex-col h-[460px] max-h-[80vh]">
          {/* Search Input */}
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
                "font-normal"
              )}
              autoFocus
            />
          </div>

          {/* Results List */}
          <div className="flex-1 overflow-y-auto px-2 py-2">
            {filteredResults.length > 0 ? (
              <div className="space-y-0">
                {filteredResults.map((result) => (
                  <button
                    key={result.id}
                    className={cn(
                      "w-full text-left px-4 py-3 rounded-lg",
                      "hover:bg-gray-50 active:bg-gray-100 transition-colors",
                      "flex items-start gap-3",
                      "cursor-pointer",
                      "border-0 outline-none focus:outline-none"
                    )}
                    onClick={() => {
                      // TODO: Navigate to chat when endpoint is ready
                      handleClose();
                    }}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <MessageSquare className="h-5 w-5 text-gray-400 stroke-[1.5]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-gray-900 mb-1 leading-tight">
                        {highlightQuery(result.title, searchQuery)}
                      </div>
                      <div className="text-xs text-gray-500 line-clamp-2 leading-relaxed">
                        {highlightQuery(result.snippet, searchQuery)}
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
