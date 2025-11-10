import { Variants } from "framer-motion";
import { Zap, Shield, MessageSquare, Bot } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
};

export const cardVariants: Variants = {
  hidden: { opacity: 0, y: 30, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
  hover: {
    y: -8,
    scale: 1.02,
    transition: {
      duration: 0.3,
      ease: "easeOut",
    },
  },
};

export const imageVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8, x: 50 },
  visible: {
    opacity: 1,
    scale: 1,
    x: 0,
    transition: {
      duration: 0.8,
      ease: "easeOut",
    },
  },
};

export const floatingVariants: Variants = {
  animate: {
    y: [0, -20, 0],
    transition: {
      duration: 4,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

export interface Feature {
  icon: LucideIcon;
  title: string;
  description: string;
}

export const features: Feature[] = [
  {
    icon: Zap,
    title: "Мгновенные ответы",
    description: "Получайте качественные ответы от AI за секунды",
  },
  {
    icon: Shield,
    title: "Безопасность данных",
    description: "Ваши данные защищены и конфиденциальны",
  },
  {
    icon: MessageSquare,
    title: "Умный диалог",
    description: "Естественное общение с искусственным интеллектом",
  },
  {
    icon: Bot,
    title: "Разнопрофильные вопросы",
    description: "Задавайте вопросы из любой области знаний",
  },
];

export const benefits: string[] = [
  "Экономия времени на поиске информации",
  "Профессиональные консультации 24/7",
  "Поддержка принятия решений",
  "Автоматизация рутинных задач",
  "Персонализированные рекомендации",
  "Масштабируемость для бизнеса",
];

