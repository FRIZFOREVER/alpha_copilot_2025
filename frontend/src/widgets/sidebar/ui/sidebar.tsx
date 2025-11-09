import { useState, useMemo } from "react";
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
import { Avatar, AvatarFallback } from "@/shared/ui/avatar";
import { cn } from "@/shared/lib/mergeClass";
import { useNavigate, useParams } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { useGetChatsQuery } from "@/entities/chat/hooks/useGetChats";
import { useCreateChatMutation } from "@/entities/chat/hooks/useCreateChat";
import { Chat } from "@/entities/chat/types/types";

export interface ChatItem {
  id: string;
  title: string;
  lastMessage?: string;
}

const userData = {
  name: "Иван Иванов",
  email: "ivan@example.com",
  avatar: null,
};

export interface SidebarProps {}

export const Sidebar = ({}: SidebarProps) => {
  const [searchQuery] = useState("");
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["chats"])
  );
  const navigate = useNavigate();
  const params = useParams<{ chatId?: string }>();
  const currentChatId = params.chatId;

  const { data: chatsData, isLoading: isLoadingChats } = useGetChatsQuery();
  const { mutate: createChat, isPending: isCreatingChat } =
    useCreateChatMutation();

  const chats: ChatItem[] = useMemo(() => {
    if (!chatsData) return [];
    return chatsData.map((chat: Chat) => ({
      id: chat.chat_id.toString(),
      title: chat.name,
      lastMessage: undefined,
    }));
  }, [chatsData]);

  const filteredChats = chats.filter((chat) =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleProfileClick = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.PROFILE_ROUTE}`);
    setIsMobileOpen(false);
  };

  const handleToggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleCloseMobile = () => {
    setIsMobileOpen(false);
  };

  const handleOpenMobile = () => {
    setIsMobileOpen(true);
  };

  const handleBackdropClick = () => {
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

  const handleNewChat = () => {
    createChat(
      { name: "Новый чат" },
      {
        onSuccess: (data) => {
          navigate(
            `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}/${data.chat_id}`
          );
          setIsMobileOpen(false);
        },
      }
    );
  };

  const handleSelectChat = (chatId: string) => {
    navigate(
      `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}/${chatId}`
    );
    setIsMobileOpen(false);
  };

  const handleMoreOptionsClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
  };

  const chatGroups = [
    {
      id: "chats",
      title: "Чаты",
      icon: MessageSquare,
      items: filteredChats,
      color: "bg-blue-500",
    },
  ];

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
          onClick={handleBackdropClick}
        />
      )}

      <aside
        className={cn(
          "fixed left-0 top-0 h-full z-50 flex flex-col transition-all duration-300",
          "bg-zinc-50",
          "md:static md:z-auto",
          isCollapsed ? "w-16 md:w-16" : "w-64 md:w-72",
          isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
      >
        <div className="flex items-center justify-between px-3.5 py-3 pb-1">
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
              onClick={handleToggleCollapse}
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
              onClick={handleCloseMobile}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
        {isCollapsed && (
          <div className="p-3 border-b border-gray-200/50 flex justify-center">
            <button
              onClick={handleNewChat}
              disabled={isCreatingChat}
              className="h-9 w-9 rounded-xl bg-white border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 shadow-sm hover:shadow-md flex items-center justify-center group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus className="h-3 w-3" />
            </button>
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
            <div className="px-2 space-y-0">
              <button
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm flex items-center gap-3"
                )}
              >
                <span className="text-zinc-500 font-medium">Обзор</span>
              </button>
              <button
                onClick={handleNewChat}
                disabled={isCreatingChat}
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm flex items-center gap-3",
                  "text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                <SquarePen className="h-5 w-5 text-gray-500" />
                <span>Новый чат</span>
              </button>
              <button
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm flex items-center gap-3",
                  "text-gray-700 hover:bg-gray-100"
                )}
              >
                <Search className="h-5 w-5 text-gray-500" />
                <span>Поиск в чатах</span>
              </button>
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
                  "text-gray-700"
                )}
              >
                <Eye className="h-5 w-5 text-gray-500" />
                <span>Insights</span>
              </button>

              {chatGroups.map((group) => {
                const isExpanded = expandedSections.has(group.id);

                return (
                  <div key={group.id}>
                    <button
                      onClick={() => toggleSection(group.id)}
                      className={cn(
                        "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm flex items-center gap-3"
                      )}
                    >
                      <span className="text-zinc-500 font-medium flex-1">
                        Чаты
                      </span>
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      )}
                    </button>

                    {isExpanded && group.items.length > 0 && (
                      <div className="mt-1 space-y-0.5">
                        {group.items.map((chat) => {
                          const isActive = currentChatId === chat.id;
                          const chatColor = getChatIcon(chat.id);
                          const chatInitial = getChatInitial(chat.title);

                          return (
                            <button
                              key={chat.id}
                              onClick={() => handleSelectChat(chat.id)}
                              className={cn(
                                "w-full text-left px-3 py-2 rounded-lg transition-all text-sm flex items-center gap-3",
                                isActive
                                  ? "bg-zinc-200 text-gray-900"
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

              {isLoadingChats ? (
                <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
                  <MessageSquare className="h-12 w-12 text-gray-300 mb-3 animate-pulse" />
                  <p className="text-sm text-gray-400">Загрузка чатов...</p>
                </div>
              ) : filteredChats.length === 0 && !searchQuery ? (
                <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
                  <MessageSquare className="h-12 w-12 text-gray-300 mb-3" />
                  <p className="text-sm text-gray-400">Нет чатов</p>
                </div>
              ) : null}
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
              className="w-full flex items-center gap-3 px-2 py-0 rounded-2xlgroup"
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
                onClick={handleMoreOptionsClick}
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
        onClick={handleOpenMobile}
      >
        <MessageSquare className="h-5 w-5" />
      </Button>
    </>
  );
};
