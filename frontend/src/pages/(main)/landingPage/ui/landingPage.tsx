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

const LandingPage = () => {
  const navigate = useNavigate();

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
    <div className="flex min-h-screen w-full flex-col bg-background">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-12 md:py-20">
        <div className="flex flex-col items-center text-center space-y-6 md:space-y-8">
          <div className="flex items-center gap-2 rounded-full bg-red-500/10 border border-red-500/20 px-4 py-2 backdrop-blur-md">
            <Sparkles className="h-4 w-4 text-red-500" />
            <span className="text-sm font-medium text-red-500">
              AI Copilot для бизнеса
            </span>
          </div>

          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground leading-tight">
            Ваш персональный <span className="text-red-500">AI ассистент</span>
          </h1>

          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl">
            Задавайте разнопрофильные вопросы к LLM и получайте качественные
            ответы. Идеальное решение для микробизнеса.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 mt-4">
            <Button
              onClick={() => navigate(`/${ERouteNames.DASHBOARD_ROUTE}`)}
              className="rounded-2xl bg-gradient-to-br from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg shadow-red-500/30 px-8 py-6 text-lg"
            >
              Начать работу
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate(`/${ERouteNames.AUTH_ROUTE}`)}
              className="rounded-2xl border-red-500/30 hover:bg-red-500/10 hover:text-red-500 px-8 py-6 text-lg"
            >
              Войти
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-12 md:py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Возможности <span className="text-red-500">платформы</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Все необходимое для эффективной работы с AI ассистентом
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="rounded-3xl border-0 md:border md:border-white/20 dark:md:border-white/10 bg-white/40 dark:bg-black/40 backdrop-blur-2xl p-6 shadow-lg shadow-red-500/5 hover:shadow-xl hover:shadow-red-500/10 transition-all"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-red-500/20 to-red-500/10 border border-red-500/30 mb-4">
                <feature.icon className="h-6 w-6 text-red-500" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Benefits Section */}
      <section className="container mx-auto px-4 py-12 md:py-20">
        <div className="rounded-3xl border border-border bg-card backdrop-blur-sm p-8 md:p-12 shadow-lg">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
                Преимущества для{" "}
                <span className="text-red-500">вашего бизнеса</span>
              </h2>
              <p className="text-muted-foreground mb-6">
                AI Copilot помогает представителям микробизнеса решать задачи
                быстрее и эффективнее, предоставляя качественные ответы на любые
                вопросы.
              </p>
              <Button
                onClick={() => navigate(ERouteNames.DASHBOARD_ROUTE)}
                className="rounded-2xl bg-gradient-to-br from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg shadow-red-500/30"
              >
                Попробовать сейчас
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {benefits.map((benefit, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 rounded-2xl bg-muted border border-border p-4"
                >
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-red-500/10 border border-red-500/20 mt-0.5">
                    <Check className="h-4 w-4 text-red-500" />
                  </div>
                  <p className="text-sm font-medium text-foreground">
                    {benefit}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-12 md:py-20">
        <div className="rounded-3xl border border-border bg-red-50 dark:bg-red-500/10 backdrop-blur-sm p-8 md:p-12 text-center shadow-lg">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Готовы начать?
          </h2>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Присоединяйтесь к тысячам пользователей, которые уже используют AI
            Copilot для развития своего бизнеса
          </p>
          <Button
            onClick={() => navigate(ERouteNames.DASHBOARD_ROUTE)}
            className="rounded-2xl bg-gradient-to-br from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg shadow-red-500/30 px-8 py-6 text-lg"
          >
            Начать бесплатно
            <ArrowRight className="h-5 w-5 ml-2" />
          </Button>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
