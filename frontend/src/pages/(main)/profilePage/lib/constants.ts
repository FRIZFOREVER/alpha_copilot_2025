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
    { name: "Альфа-Бизнес", connected: true, icon: "🏦" },
    { name: "Telegram", connected: true, icon: "💬" },
    { name: "Email", connected: true, icon: "📧" },
    { name: "CRM", connected: false, icon: "📊" },
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
