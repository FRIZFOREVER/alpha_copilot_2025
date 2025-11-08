import { useState } from "react";
import { Chat } from "@/features/chat";
import { Sidebar } from "@/widgets/sidebar";

const DashboardPage = () => {
  const [currentChatId, setCurrentChatId] = useState<string | undefined>("1");

  const mockChats = [
    { id: "1", title: "Новый чат", lastMessage: "Привет! Расскажи о себе" },
    {
      id: "2",
      title: "Решение проблемы с кодом",
      lastMessage: "Как исправить ошибку...",
    },
    { id: "3", title: "Вопросы по бизнесу", lastMessage: "Какие стратегии..." },
    {
      id: "4",
      title: "Анализ данных",
      lastMessage: "Помоги проанализировать...",
    },
  ];

  const mockMessages = [
    {
      id: "1",
      content: "Привет! Я AI ассистент. Чем могу помочь?",
      isUser: false,
      timestamp: "10:00",
    },
    {
      id: "2",
      content: "Привет! Расскажи о себе",
      isUser: true,
      timestamp: "10:01",
    },
    {
      id: "3",
      content:
        "Я современный AI ассистент, созданный для помощи в различных задачах. Могу отвечать на вопросы, помогать с кодом, анализировать данные и многое другое!",
      isUser: false,
      timestamp: "10:02",
    },
  ];

  const handleSendMessage = (message: string) => {
    // Логика отправки сообщения будет добавлена позже
    console.log("Отправка сообщения:", message);
  };

  const handleNewChat = () => {
    // Логика создания нового чата
    console.log("Создание нового чата");
  };

  const handleSelectChat = (chatId: string) => {
    setCurrentChatId(chatId);
    // Логика загрузки чата
    console.log("Выбран чат:", chatId);
  };

  return (
    <div className="flex h-full w-full bg-background">
      <Sidebar
        chats={mockChats}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        currentChatId={currentChatId}
      />
      <div className="flex-1 flex flex-col overflow-hidden border-l border-sidebar-border bg-background">
        <Chat
          messages={mockMessages}
          onSendMessage={handleSendMessage}
          isLoading={false}
        />
      </div>
    </div>
  );
};

export default DashboardPage;
