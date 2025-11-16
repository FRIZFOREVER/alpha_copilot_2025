import { useState, useMemo } from "react";
import {
  Search,
  MessageSquare,
  X,
  ChevronDown,
  ChevronRight,
  ChartArea,
  SquarePen,
  Clock,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/shared/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/shared/ui/avatar";
import { cn } from "@/shared/lib/mergeClass";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { useGetChatsQuery } from "@/entities/chat/hooks/useGetChats";
import { Chat } from "@/entities/chat/types/types";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import { useModal } from "@/shared/lib/modal/context";
import { EModalVariables } from "@/shared/lib/modal/constants";
import {
  getUserInitials,
  getDisplayName,
} from "@/shared/lib/utils/userHelpers";
import { Icon, IconTypes } from "@/shared/ui/icon";
import { useChatCollapse } from "@/shared/lib/chatCollapse";

export interface ChatItem {
  id: string;
  title: string;
  lastMessage?: string;
}

export const Sidebar = () => {
  const [searchQuery] = useState("");
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["chats"])
  );
  const [hoveredHistoryButton, setHoveredHistoryButton] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams<{ chatId?: string }>();
  const currentChatId = params.chatId;
  const { isCollapsed: isChatCollapsed } = useChatCollapse();

  const { data: chatsData, isLoading: isLoadingChats } = useGetChatsQuery();
  const { data: profileData } = useGetProfileQuery();
  const { openModal } = useModal();

  const isChatRoute =
    location.pathname.includes(`/${ERouteNames.CHAT_ROUTE}`) ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}` ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}/`;

  const shouldHideSidebar = isChatCollapsed && isChatRoute;

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

  const handleSelectChat = (chatId: string) => {
    navigate(
      `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}/${chatId}`
    );
    setIsMobileOpen(false);
  };

  const handleNewChat = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}`);
    setIsMobileOpen(false);
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

  const displayName = profileData?.username
    ? getDisplayName(profileData.username)
    : "Пользователь";
  const displayEmail = profileData?.login || "";
  const userInitials = profileData?.username
    ? getUserInitials(profileData.username)
    : "П";

  return (
    <>
      {isMobileOpen && !shouldHideSidebar && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
          onClick={handleBackdropClick}
        />
      )}

      <aside
        className={cn(
          "fixed left-0 top-0 h-full z-50 flex flex-col transition-all duration-300 rounded-r-xl md:rounded-r-none",
          "bg-[#f9f9f9]",
          "md:static md:z-auto",
          isCollapsed ? "w-16 md:w-16" : "w-64",
          isMobileOpen && !shouldHideSidebar
            ? "translate-x-0"
            : "-translate-x-full md:translate-x-0",
          shouldHideSidebar && "hidden md:hidden"
        )}
      >
        <div className="flex items-center justify-between px-3.5 py-3 pb-2.5">
          <div
            className={cn(
              "flex items-center justify-start w-full",
              isCollapsed ? "justify-center" : "justify-start"
            )}
          >
            <div className="group cursor-pointer rounded-lg transition-all duration-300 hover:bg-red-50/50">
              <Icon
                type={IconTypes.LOGO_OUTLINED_V2}
                className="text-3xl text-red-400 fill-red-100/80 stroke-red-200 transition-all duration-300 group-hover:scale-110 group-hover:text-red-600 group-hover:fill-red-200 group-hover:stroke-red-300 group-hover:drop-shadow-lg"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-lg hover:bg-gray-100 text-gray-600 hidden md:flex cursor-pointer"
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
        <div className="flex-1 overflow-y-auto py-2">
          {isCollapsed ? (
            <div className="flex flex-col items-center gap-1 px-2">
              <button
                className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center transition-all cursor-pointer",
                  "text-gray-600 hover:bg-gray-100"
                )}
                onClick={() => {
                  openModal(EModalVariables.SEARCH_CHATS_MODAL);
                }}
                title="Поиск в чатах"
              >
                <Search className="h-5 w-5" />
              </button>
              <button
                onClick={handleNewChat}
                className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center transition-all cursor-pointer",
                  "text-gray-600 hover:bg-gray-100"
                )}
                title="Новый чат"
              >
                <SquarePen className="h-5 w-5" />
              </button>
              <button
                onClick={() => {
                  navigate(
                    `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.ANALYTICS_ROUTE}`
                  );
                  setIsMobileOpen(false);
                }}
                className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center transition-all cursor-pointer",
                  "text-gray-600 hover:bg-gray-100"
                )}
                title="Аналитика"
              >
                <ChartArea className="h-5 w-5" />
              </button>
            </div>
          ) : (
            <div className="px-2 space-y-1">
              <button
                onClick={() => {
                  openModal(EModalVariables.SEARCH_CHATS_MODAL);
                }}
                className={cn(
                  "w-full text-left px-3 border py-[9px] rounded-4xl transition-all text-sm flex items-center gap-1.5 cursor-pointer bg-[#0000000f]/60",
                  "text-gray-700"
                )}
              >
                <Search className="h-[18px] w-[18px] text-gray-500" />
                <span>Поиск</span>
              </button>

              <button
                onClick={handleNewChat}
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-3xl transition-all text-sm flex items-center gap-1.5 cursor-pointer",
                  "text-gray-700 hover:bg-[#0000000f]/60"
                )}
              >
                <SquarePen className="h-[18px] w-[18px] text-gray-500" />
                <span>Новый чат</span>
              </button>

              <button
                onClick={() => {
                  navigate(
                    `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.ANALYTICS_ROUTE}`
                  );
                  setIsMobileOpen(false);
                }}
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-3xl transition-all text-sm flex items-center gap-1.5 cursor-pointer",
                  "text-gray-700 hover:bg-[#0000000f]/60"
                )}
              >
                <ChartArea className="h-[18px] w-[18px] text-gray-500" />
                <span>Аналитика</span>
              </button>

              {chatGroups.map((group) => {
                const isExpanded = expandedSections.has(group.id);

                return (
                  <div key={group.id}>
                    <button
                      onClick={() => toggleSection(group.id)}
                      onMouseEnter={() => setHoveredHistoryButton(true)}
                      onMouseLeave={() => setHoveredHistoryButton(false)}
                      className={cn(
                        "w-full text-left px-2 py-2 gap-0.5 hover:bg-[#0000000f]/60 cursor-pointer rounded-3xl transition-all text-sm flex items-center"
                      )}
                      disabled={!filteredChats.length}
                    >
                      <span className="rounded-full p-1 hover:bg-[#0000000f]/80 transition-all duration-300">
                        {hoveredHistoryButton ? (
                          isExpanded ? (
                            <ChevronRight className="h-[18px] w-[18px] text-gray-400 cursor-pointer" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-gray-400 cursor-pointer" />
                          )
                        ) : (
                          <Clock className="h-[18px] w-[18px] text-gray-400" />
                        )}
                      </span>

                      <span className="text-zinc-500 font-medium flex-1">
                        История
                      </span>
                    </button>

                    <AnimatePresence>
                      {isExpanded && group.items.length > 0 && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2, ease: "easeInOut" }}
                          className="overflow-hidden"
                        >
                          <div className="mt-1 space-y-0.5 ml-[21px] pl-[8px] border-l">
                            {group.items.map((chat) => {
                              const isActive = currentChatId === chat.id;

                              return (
                                <button
                                  key={chat.id}
                                  onClick={() => handleSelectChat(chat.id)}
                                  className={cn(
                                    "w-full text-left px-3 py-2 rounded-2xl transition-all text-sm flex items-center gap-3 cursor-pointer hover:bg-[#0000000f]/60",
                                    isActive && "bg-[#0000000f] text-gray-900"
                                  )}
                                >
                                  <span className="truncate flex-1 text-gray-700">
                                    {chat.title}
                                  </span>
                                  {isActive && (
                                    <ChevronRight className="h-4 w-4 text-gray-400" />
                                  )}
                                </button>
                              );
                            })}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })}

              {isLoadingChats && (
                <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
                  <MessageSquare className="h-12 w-12 text-gray-300 mb-3 animate-pulse" />
                  <p className="text-sm text-gray-400">Загрузка чатов...</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div
          className={cn(
            "py-2 border-t border-gray-200/50 hover:bg-[#0000000f] bg-[#0000000f]/60 rounded-3xl m-2",
            isCollapsed && "bg-[#f9f9f9]"
          )}
        >
          {isCollapsed ? (
            <div className="flex flex-col items-center gap-2 cursor-pointer">
              <button
                onClick={handleProfileClick}
                className="h-10 w-10 rounded-lg transition-all flex items-center justify-center cursor-pointer"
              >
                <Avatar className="h-10 w-10 border-2 border-gray-200 bg-gradient-to-br from-red-500 to-pink-500 rounded-full shrink-0">
                  <AvatarImage
                    src="/images/user.webp"
                    alt={displayName}
                    className="object-cover rounded-full"
                  />
                </Avatar>
              </button>
            </div>
          ) : (
            <button
              onClick={handleProfileClick}
              className="w-full flex items-center gap-2 px-2 py-0 rounded-2xl group cursor-pointer"
            >
              <Avatar className="h-10 w-10 border-2 border-gray-200 bg-gradient-to-br from-red-500 to-pink-500 rounded-full shrink-0">
                <AvatarImage
                  src="/images/user.webp"
                  alt={displayName}
                  className="object-cover rounded-full"
                />
                <AvatarFallback className="bg-gradient-to-br from-red-500 to-pink-500 text-white rounded-full text-xs font-semibold">
                  {userInitials}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {displayName}
                </p>
                <p className="text-xs text-gray-500 truncate">{displayEmail}</p>
              </div>
            </button>
          )}
        </div>
      </aside>

      {!shouldHideSidebar && (
        <Button
          variant="ghost"
          size="icon"
          className="fixed cursor-pointer top-2.5 left-2 z-30 md:hidden h-10 w-10 rounded-xl bg-white/40 dark:bg-black/40 backdrop-blur-md border border-white/20"
          onClick={handleOpenMobile}
        >
          <Icon type={IconTypes.MENU_OUTLINED} />
        </Button>
      )}
    </>
  );
};
