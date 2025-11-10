import { Zap, Target, Star, Crown } from "lucide-react";

export const mockData = {
  joinDate: "15 января 2024",
  plan: "Pro",
  level: 5,
  xp: 1247,
  xpToNext: 1500,
  usage: {
    messages: 1247,
    chats: 24,
    daysActive: 12,
  },
  achievements: [
    { icon: Zap, label: "Молния", unlocked: true },
    { icon: Star, label: "Звезда", unlocked: true },
    { icon: Crown, label: "Корона", unlocked: false },
    { icon: Target, label: "Цель", unlocked: true },
  ],
};
