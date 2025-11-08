import { useState } from "react";
import {
  Plus,
  Search,
  MessageSquare,
  X,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  Home,
  Eye,
  Bot,
  Zap,
  MoreVertical,
  SquarePen,
} from "lucide-react";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Avatar, AvatarFallback } from "@/shared/ui/avatar";
import { cn } from "@/shared/lib/mergeClass";
import { useNavigate } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";

export interface ChatItem {
  id: string;
  title: string;
  lastMessage?: string;
}

export interface SidebarProps {
  chats?: ChatItem[];
  onNewChat?: () => void;
  onSelectChat?: (chatId: string) => void;
  currentChatId?: string;
}

export const Sidebar = ({
  chats = [],
  onNewChat,
  onSelectChat,
  currentChatId,
}: SidebarProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["chats"])
  );
  const navigate = useNavigate();

  // Моковые данные пользователя
  const userData = {
    name: "Иван Иванов",
    email: "ivan@example.com",
    avatar: null,
  };

  const filteredChats = chats.filter((chat) =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleProfileClick = () => {
    navigate(ERouteNames.PROFILE_ROUTE);
    setIsMobileOpen(false);
  };

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  // Группируем чаты для демонстрации (можно адаптировать под реальные данные)
  const chatGroups = [
    {
      id: "chats",
      title: "Чаты",
      icon: MessageSquare,
      items: filteredChats,
      color: "bg-blue-500",
    },
  ];

  // Генерируем цветные иконки для чатов
  const getChatIcon = (chatId: string) => {
    const colors = [
      "bg-blue-500",
      "bg-purple-500",
      "bg-green-500",
      "bg-orange-500",
      "bg-pink-500",
      "bg-indigo-500",
    ];
    const index = parseInt(chatId) % colors.length;
    return colors[index];
  };

  const getChatInitial = (title: string) => {
    return title.charAt(0).toUpperCase();
  };

  return (
    <>
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed left-0 top-0 h-full z-50 flex flex-col transition-all duration-300",
          "bg-white border-r border-gray-200/50",
          "md:static md:z-auto",
          isCollapsed ? "w-16 md:w-16" : "w-64 md:w-72",
          isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
      >
        <div className="flex items-center justify-between p-3.5 min-h-[60px]">
          <div
            className={cn(
              "flex items-center justify-start w-full",
              isCollapsed ? "justify-center" : "justify-start"
            )}
          >
            <Zap className="h-6 w-6 text-blue-500" />
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-lg hover:bg-gray-100 text-gray-600 hidden md:flex"
              onClick={() => setIsCollapsed(!isCollapsed)}
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4 rotate-180" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden h-8 w-8 rounded-lg hover:bg-gray-100 text-gray-600"
              onClick={() => setIsMobileOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {!isCollapsed && (
          <div className="p-3 border-gray-200/50">
            <button
              onClick={() => {
                onNewChat?.();
                setIsMobileOpen(false);
              }}
              className="w-full rounded-2xl bg-white border text-zinc-700 border-gray-200 hover:border-gray-300 hover:bg-gray-50 h-10 transition-all duration-200 font-medium flex items-center justify-center gap-2 group"
            >
              <SquarePen className="h-4 w-4" />
              <span>Новый чат</span>
            </button>
          </div>
        )}

        {isCollapsed && (
          <div className="p-3 border-b border-gray-200/50 flex justify-center">
            <button
              onClick={() => {
                onNewChat?.();
                setIsMobileOpen(false);
              }}
              className="h-9 w-9 rounded-xl bg-white border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 shadow-sm hover:shadow-md flex items-center justify-center group"
            >
              <Plus className="h-3 w-3" />
            </button>
          </div>
        )}

        {!isCollapsed && (
          <div className="px-3 pb-3 border-b border-gray-200/50">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Поиск..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 h-9 rounded-2xl border-gray-200 text-gray-900 placeholder:text-gray-400 focus-visible:ring-blue-500/20 focus-visible:border-blue-500"
              />
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto py-2">
          {isCollapsed ? (
            <div className="flex flex-col items-center gap-1 px-2">
              <button
                className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center transition-all",
                  "text-gray-600 hover:bg-gray-100"
                )}
              >
                <Home className="h-5 w-5" />
              </button>
              <button
                className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center transition-all",
                  "text-gray-600 hover:bg-gray-100"
                )}
              >
                <Eye className="h-5 w-5" />
              </button>
              <button
                className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center transition-all",
                  expandedSections.has("chats")
                    ? "bg-gray-100 text-gray-900"
                    : "text-gray-600 hover:bg-gray-100"
                )}
                onClick={() => toggleSection("chats")}
              >
                <Bot className="h-5 w-5" />
              </button>
            </div>
          ) : (
            <div className="px-2 space-y-1">
              <button
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm flex items-center gap-3",
                  "text-gray-700 hover:bg-gray-100"
                )}
              >
                <Home className="h-5 w-5 text-gray-500" />
                <span>Home</span>
              </button>

              <button
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm flex items-center gap-3",
                  "bg-gray-100 text-gray-900"
                )}
              >
                <Eye className="h-5 w-5 text-gray-500" />
                <span>Insights</span>
              </button>

              {chatGroups.map((group) => {
                const isExpanded = expandedSections.has(group.id);
                const Icon = group.icon;

                return (
                  <div key={group.id}>
                    <button
                      onClick={() => toggleSection(group.id)}
                      className={cn(
                        "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm flex items-center gap-3",
                        isExpanded
                          ? "bg-gray-100 text-gray-900"
                          : "text-gray-700 hover:bg-gray-50"
                      )}
                    >
                      <Icon className="h-5 w-5 text-gray-500 shrink-0" />
                      <span className="flex-1">Chat bots</span>
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      )}
                    </button>

                    {isExpanded && group.items.length > 0 && (
                      <div className="ml-4 mt-1 space-y-0.5">
                        {group.items.map((chat) => {
                          const isActive = currentChatId === chat.id;
                          const chatColor = getChatIcon(chat.id);
                          const chatInitial = getChatInitial(chat.title);

                          return (
                            <button
                              key={chat.id}
                              onClick={() => {
                                onSelectChat?.(chat.id);
                                setIsMobileOpen(false);
                              }}
                              className={cn(
                                "w-full text-left px-3 py-2 rounded-lg transition-all text-sm flex items-center gap-3",
                                isActive
                                  ? "bg-gray-100 text-gray-900"
                                  : "text-gray-600 hover:bg-gray-50"
                              )}
                            >
                              <div
                                className={cn(
                                  "h-6 w-6 rounded-full flex items-center justify-center text-white text-xs font-medium shrink-0",
                                  chatColor
                                )}
                              >
                                {chatInitial}
                              </div>
                              <span className="truncate flex-1">
                                {chat.title}
                              </span>
                              {isActive && (
                                <ChevronRight className="h-4 w-4 text-gray-400" />
                              )}
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}

              {filteredChats.length === 0 && !searchQuery && (
                <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
                  <MessageSquare className="h-12 w-12 text-gray-300 mb-3" />
                  <p className="text-sm text-gray-400">Нет чатов</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="p-3 border-t border-gray-200/50">
          {isCollapsed ? (
            <div className="flex flex-col items-center gap-2">
              <button
                onClick={handleProfileClick}
                className="h-10 w-10 rounded-lg hover:bg-gray-100 transition-all flex items-center justify-center"
              >
                <Avatar className="h-8 w-8 border-2 border-gray-200 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg">
                  <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white rounded-lg text-xs font-semibold">
                    {userData.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </AvatarFallback>
                </Avatar>
              </button>
            </div>
          ) : (
            <button
              onClick={handleProfileClick}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-2xl bg-white border border-gray-200 group"
            >
              <Avatar className="h-10 w-10 border-2 border-gray-200 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full shrink-0">
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white rounded-full text-xs font-semibold">
                  {userData.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {userData.name}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {userData.email}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                }}
                className="h-8 w-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-all shrink-0"
              >
                <MoreVertical className="h-4 w-4" />
              </button>
            </button>
          )}
        </div>
      </aside>

      <Button
        variant="ghost"
        size="icon"
        className="fixed top-4 left-4 z-30 md:hidden h-10 w-10 rounded-xl bg-white/40 dark:bg-black/40 backdrop-blur-md border border-white/20"
        onClick={() => setIsMobileOpen(true)}
      >
        <MessageSquare className="h-5 w-5" />
      </Button>
    </>
  );
};
