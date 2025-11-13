import { Variants } from "framer-motion";
import {
  Zap,
  MessageSquare,
  Clock,
  FileText,
  TrendingUp,
  Users,
} from "lucide-react";
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
    icon: FileText,
    title: "Работа с документами",
    description:
      "Создавайте и редактируйте письма, договоры и презентации с помощью AI",
  },
  {
    icon: Clock,
    title: "Экономия времени",
    description: "Автоматизируйте рутинные задачи и фокусируйтесь на стратегии",
  },
  {
    icon: MessageSquare,
    title: "24/7 Поддержка",
    description:
      "Получайте ответы на вопросы в любое время, прямо в мессенджере",
  },
  {
    icon: TrendingUp,
    title: "Аналитика и рекомендации",
    description:
      "Анализируйте данные и получайте рекомендации для развития бизнеса",
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

export interface Statistic {
  icon: LucideIcon;
  value: string;
  label: string;
}

export const statistics: Statistic[] = [
  {
    icon: Users,
    value: "1000+",
    label: "Активных пользователей",
  },
  {
    icon: Clock,
    value: "24/7",
    label: "Доступность сервиса",
  },
  {
    icon: Zap,
    value: "99.9%",
    label: "Надежность системы",
  },
];

export interface Testimonial {
  quote: string;
  author: string;
  role: string;
  avatar?: string;
}

export const testimonials: Testimonial[] = [
  {
    quote:
      "AI Copilot помог мне сократить время на обработку документов на 70%. Теперь я могу больше времени уделять клиентам и развитию бизнеса.",
    author: "Мария Иванова",
    role: "Владелец кофейни",
  },
  {
    quote:
      "Отличный помощник для малого бизнеса! Быстро получаю ответы на юридические и финансовые вопросы, не тратя время на поиск информации.",
    author: "Алексей Петров",
    role: "Директор салона красоты",
  },
  {
    quote:
      "Использую для создания контента и анализа данных. Сервис стал незаменимым инструментом в моей ежедневной работе.",
    author: "Елена Смирнова",
    role: "Предприниматель",
  },
];
