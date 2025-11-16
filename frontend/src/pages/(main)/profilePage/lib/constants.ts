import {
  Zap,
  Target,
  Star,
  Crown,
  FileText,
  CheckCircle2,
  Sparkles,
  TrendingUp,
} from "lucide-react";

export const mockData = {
  joinDate: "15 января 2024",
  plan: "Pro",
  level: 5,
  xp: 1247,
  xpToNext: 1500,
  business: {
    name: "Кофейня 'Уютная'",
    type: "Кафе и рестораны",
    industry: "Общественное питание",
  },
  usage: {
    messages: 1247,
    chats: 24,
    daysActive: 12,
  },
  productivity: {
    tasksCompleted: 156,
    timeSaved: "42 часа",
    documentsCreated: 23,
    templatesUsed: 8,
  },
  integrations: [
    {
      name: "Todoist",
      connected: false,
      icon: "🏦",
      imageSrc: "/images/D03_CardPromo1_210325.webp",
      description: "Управление задачами, проектами, списками и многое другое",
      category: "ДЛЯ ЛЮБЫХ СОТРУДНИКОВ",
      isDevelopment: false,
    },
    {
      name: "Telegram",
      connected: true,
      icon: "💬",
      imageSrc: "/images/D03_CardPromo2_210325.webp",
      description:
        "Обмен сообщениями, уведомления, быстрая связь с командой и клиентами",
      category: "КОММУНИКАЦИИ",
      isDevelopment: false,
    },
    {
      name: "Email",
      connected: false,
      icon: "📧",
      imageSrc: "/images/D04_CardPromo3_210325.webp",
      description:
        "Отправка и получение писем, автоматизация рассылок, управление корреспонденцией",
      category: "КОРРЕСПОНДЕНЦИЯ",
      isDevelopment: true,
    },
    {
      name: "CRM",
      connected: false,
      icon: "📊",
      imageSrc: "/images/D04_CardPromo2_210325.webp",
      description:
        "Управление клиентами, аналитика продаж, автоматизация бизнес-процессов",
      category: "УПРАВЛЕНИЕ",
      isDevelopment: true,
    },
  ],
  topFeatures: [
    { name: "Создание документов", count: 45, icon: FileText },
    { name: "Финансовые вопросы", count: 32, icon: TrendingUp },
    { name: "Маркетинг", count: 28, icon: Sparkles },
    { name: "Юридические вопросы", count: 15, icon: CheckCircle2 },
  ],
  recommendations: [
    {
      title: "Подключите CRM для анализа продаж",
      description: "Получайте автоматические рекомендации по оптимизации",
      action: "Подключить",
    },
    {
      title: "Создайте шаблон для договоров",
      description: "Экономьте время на оформлении документов",
      action: "Создать",
    },
  ],
  achievements: [
    { icon: Zap, label: "Молния", unlocked: true },
    { icon: Star, label: "Звезда", unlocked: true },
    { icon: Crown, label: "Корона", unlocked: false },
    { icon: Target, label: "Цель", unlocked: true },
  ],
};
