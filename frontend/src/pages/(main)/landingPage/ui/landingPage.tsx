import {
  Sparkles,
  Zap,
  Shield,
  MessageSquare,
  ArrowRight,
  Bot,
  Check,
} from "lucide-react";
import { Button } from "@/shared/ui/button";
import { useNavigate } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import { getAccessToken } from "@/entities/token/lib/tokenService";
import { useMemo } from "react";
import { motion, Variants } from "framer-motion";
import { Image } from "@/shared/ui/image/image";

const LandingPage = () => {
  const navigate = useNavigate();
  const token = getAccessToken();
  const { data: profileData, isSuccess: isProfileSuccess } =
    useGetProfileQuery();

  const isAuthenticated = useMemo(() => {
    return !!token && isProfileSuccess && !!profileData;
  }, [token, isProfileSuccess, profileData]);

  const handleStartWork = () => {
    if (isAuthenticated) {
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    } else {
      navigate(`/${ERouteNames.AUTH_ROUTE}/${ERouteNames.REGISTER_ROUTE}`);
    }
  };

  // Animation variants
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants: Variants = {
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

  const cardVariants: Variants = {
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

  const imageVariants: Variants = {
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

  const floatingVariants: Variants = {
    animate: {
      y: [0, -20, 0],
      transition: {
        duration: 4,
        repeat: Infinity,
        ease: "easeInOut",
      },
    },
  };

  const features = [
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

  const benefits = [
    "Экономия времени на поиске информации",
    "Профессиональные консультации 24/7",
    "Поддержка принятия решений",
    "Автоматизация рутинных задач",
    "Персонализированные рекомендации",
    "Масштабируемость для бизнеса",
  ];

  return (
    <div className="flex min-h-screen w-full flex-col bg-background overflow-hidden">
      <section className="container mx-auto px-4 py-12 md:py-20 relative">
        <div className="absolute inset-0 -z-10 bg-gradient-to-br from-red-500/5 via-transparent to-pink-500/5 blur-3xl" />
        <motion.div
          className="flex flex-col lg:flex-row items-center gap-12 lg:gap-16"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="flex-1 flex flex-col items-center lg:items-start text-center lg:text-left space-y-6 md:space-y-8">
            <motion.div
              variants={itemVariants}
              className="flex items-center gap-2 rounded-full bg-red-500/10 border border-red-500/20 px-4 py-2 backdrop-blur-md"
            >
              <Sparkles className="h-4 w-4 text-red-500 animate-pulse" />
              <span className="text-sm font-medium text-red-500">
                AI Copilot для бизнеса
              </span>
            </motion.div>

            <motion.h1
              variants={itemVariants}
              className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground leading-tight"
            >
              Ваш персональный{" "}
              <span className="bg-gradient-to-r from-red-500 to-pink-600 bg-clip-text text-transparent">
                AI ассистент
              </span>
            </motion.h1>

            <motion.p
              variants={itemVariants}
              className="text-lg md:text-xl text-muted-foreground max-w-2xl"
            >
              Задавайте разнопрофильные вопросы к LLM и получайте качественные
              ответы. Идеальное решение для микробизнеса.
            </motion.p>

            <motion.div
              variants={itemVariants}
              className="flex flex-col sm:flex-row gap-4 mt-4"
            >
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  onClick={handleStartWork}
                  className="rounded-2xl bg-gradient-to-br cursor-pointer from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg shadow-red-500/30 px-8 py-6 text-lg"
                >
                  Начать работу
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </motion.div>
              {!isAuthenticated && (
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    variant="outline"
                    onClick={() => navigate(`/${ERouteNames.AUTH_ROUTE}`)}
                    className="rounded-2xl cursor-pointer border-red-500/30 hover:bg-red-500/10 hover:text-red-500 px-8 py-6 text-lg"
                  >
                    Войти
                  </Button>
                </motion.div>
              )}
            </motion.div>
          </div>

          <motion.div
            variants={imageVariants}
            className="flex-1 flex items-center justify-center relative"
          >
            <div className="relative">
              <div className="absolute inset-0 rounded-full blur-3xl animate-pulse scale-150" />
              <motion.div variants={floatingVariants} animate="animate">
                <Image
                  src="/images/meditation-yaga.png"
                  alt="AI Assistant"
                  className="w-64 md:w-80 lg:w-96 h-auto drop-shadow-2xl select-none relative z-10"
                />
              </motion.div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      <section className="container mx-auto px-4 py-12 md:py-20 relative">
        <div className="absolute inset-0 -z-10 bg-gradient-to-t from-red-500/3 via-transparent to-transparent" />
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
        >
          <motion.div variants={itemVariants} className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Возможности{" "}
              <span className="bg-gradient-to-r from-red-500 to-pink-600 bg-clip-text text-transparent">
                платформы
              </span>
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Все необходимое для эффективной работы с AI ассистентом
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={cardVariants}
                whileHover="hover"
                className="rounded-3xl border-0 md:border md:border-white/20 dark:md:border-white/10 bg-white/40 dark:bg-black/40 backdrop-blur-2xl p-6 shadow-lg shadow-red-500/5 hover:shadow-xl hover:shadow-red-500/20 transition-all cursor-pointer group"
              >
                <motion.div
                  className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-red-500/20 to-red-500/10 border border-red-500/30 mb-4 group-hover:from-red-500/30 group-hover:to-red-500/20 transition-colors"
                  whileHover={{ rotate: [0, -10, 10, -10, 0] }}
                  transition={{ duration: 0.5 }}
                >
                  <feature.icon className="h-6 w-6 text-red-500" />
                </motion.div>
                <h3 className="text-xl font-semibold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      <section className="container mx-auto px-4 py-12 md:py-20 relative">
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-transparent via-red-500/5 to-transparent" />
        <motion.div
          className="rounded-3xl border border-border bg-card backdrop-blur-sm p-8 md:p-12 shadow-lg relative overflow-hidden"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
        >
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-red-500/10 to-pink-600/10 rounded-full blur-3xl -z-10" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center relative z-10">
            <motion.div variants={itemVariants}>
              <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
                Преимущества для{" "}
                <span className="bg-gradient-to-r from-red-500 to-pink-600 bg-clip-text text-transparent">
                  вашего бизнеса
                </span>
              </h2>
              <p className="text-muted-foreground mb-6">
                AI Copilot помогает представителям микробизнеса решать задачи
                быстрее и эффективнее, предоставляя качественные ответы на любые
                вопросы.
              </p>
              <Button
                onClick={handleStartWork}
                className="rounded-2xl bg-gradient-to-br cursor-pointer from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg shadow-red-500/30"
              >
                Попробовать сейчас
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </motion.div>
            <motion.div
              variants={itemVariants}
              className="flex flex-col lg:flex-row gap-8 items-center"
            >
              <motion.div
                variants={imageVariants}
                className="flex-shrink-0 hidden lg:block"
              >
                <motion.div variants={floatingVariants} animate="animate">
                  <Image
                    src="/images/question-people.png"
                    alt="Benefits"
                    className="w-48 md:w-64 h-auto drop-shadow-xl select-none"
                  />
                </motion.div>
              </motion.div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 flex-1">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={index}
                    variants={cardVariants}
                    whileHover="hover"
                    className="flex items-start gap-3 rounded-2xl bg-muted/50 border border-border p-4 backdrop-blur-sm hover:bg-muted transition-colors"
                  >
                    <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-red-500/10 border border-red-500/20 mt-0.5">
                      <Check className="h-4 w-4 text-red-500" />
                    </div>
                    <p className="text-sm font-medium text-foreground">
                      {benefit}
                    </p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </motion.div>
      </section>
      <section className="container mx-auto px-4 py-12 md:py-20 relative">
        <div className="absolute inset-0 -z-10 bg-gradient-to-t from-red-500/5 via-transparent to-transparent" />
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
        >
          <motion.div
            variants={itemVariants}
            className="rounded-3xl border border-border bg-gradient-to-br from-red-50/50 to-pink-50/50 dark:from-red-500/10 dark:to-pink-500/10 backdrop-blur-sm p-8 md:p-12 text-center shadow-lg relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-pink-600/5 rounded-3xl blur-2xl" />
            <div className="relative z-10">
              <motion.h2
                variants={itemVariants}
                className="text-3xl md:text-4xl font-bold text-foreground mb-4"
              >
                Готовы начать?
              </motion.h2>
              <motion.p
                variants={itemVariants}
                className="text-muted-foreground mb-8 max-w-2xl mx-auto"
              >
                Присоединяйтесь к тысячам пользователей, которые уже используют
                AI Copilot для развития своего бизнеса
              </motion.p>
              <motion.div
                variants={itemVariants}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  onClick={handleStartWork}
                  className="rounded-2xl bg-gradient-to-br cursor-pointer from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg shadow-red-500/30 px-8 py-6 text-lg"
                >
                  Начать бесплатно
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </motion.div>
            </div>
          </motion.div>
        </motion.div>
      </section>
    </div>
  );
};

export default LandingPage;
