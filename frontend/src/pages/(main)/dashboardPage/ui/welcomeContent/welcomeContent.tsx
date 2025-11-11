import { Sparkles, FileText, TrendingUp, Clock, MessageSquare } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";

interface FeatureCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  className?: string;
}

const FeatureCard = ({ icon: Icon, title, description, className }: FeatureCardProps) => {
  return (
    <div
      className={cn(
        "p-6 rounded-xl border border-gray-200 bg-white",
        "hover:shadow-md transition-shadow duration-200",
        className
      )}
    >
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-lg bg-purple-50 text-purple-600 flex-shrink-0">
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
          <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
        </div>
      </div>
    </div>
  );
};

export const WelcomeContent = () => {
  return (
    <div className="h-full overflow-y-auto bg-gray-50">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="mb-12">
          <div className="mb-4">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Приложение-помощник для малого бизнеса
            </h1>
            <p className="text-lg text-gray-600 leading-relaxed max-w-2xl">
              Используйте возможности ИИ для автоматизации ключевых задач вашего бизнеса.
              Экономьте время и повышайте качество управленческих решений.
            </p>
          </div>
        </div>

        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Бизнес-контекст
          </h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-700 leading-relaxed mb-4">
              Микробизнес живет в режиме необходимости постоянно принимать решения:
              оплатить счет, оформить платеж, запустить акцию, поправить договор, ответить
              клиенту, выдать сотруднику поручение. У владельца кофейни или руководителя
              салона красоты нет привычки сидеть за компьютером весь день. Его рабочие
              инструменты должны быть в кармане — в телефоне и мессенджере, — работать
              быстро и просто.
            </p>
            <p className="text-gray-700 leading-relaxed">
              Приложение-помощник для микробизнеса — это разговорный ИИ-помощник,
              встроенный в привычные рабочие инструменты. Он решает проблемы дефицита
              времени и экспертизы здесь и сейчас.
            </p>
          </div>
        </div>

        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Возможности
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FeatureCard
              icon={FileText}
              title="Документы и письма"
              description="Пишет и редактирует письма и документы, резюмирует переписку и встречи, собирает черновые презентации и таблицы"
            />
            <FeatureCard
              icon={MessageSquare}
              title="Юридические вопросы"
              description="Отвечает на типовые юридические и финансовые вопросы, предлагает шаблоны и чек-листы"
            />
            <FeatureCard
              icon={TrendingUp}
              title="Маркетинг и аналитика"
              description="Помогает с маркетингом (посты, промомеханики), анализирует операционные данные (продажи, остатки, платежи) и рекомендует следующие шаги"
            />
            <FeatureCard
              icon={Clock}
              title="Экономия времени"
              description="У владельца бизнеса уходит меньше времени на операционные задачи и больше — на стратегию и работу с людьми"
            />
          </div>
        </div>

        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Примеры на рынке
          </h2>
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-white border border-gray-200">
              <div className="flex items-start gap-3">
                <Sparkles className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Microsoft 365 Copilot
                  </h3>
                  <p className="text-sm text-gray-600">
                    Работает внутри Word/Excel/Outlook/Teams и ускоряет ежедневные
                    офисные процессы для малого бизнеса
                  </p>
                </div>
              </div>
            </div>
            <div className="p-4 rounded-lg bg-white border border-gray-200">
              <div className="flex items-start gap-3">
                <TrendingUp className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Intuit Assist (QuickBooks)
                  </h3>
                  <p className="text-sm text-gray-600">
                    Выступает ИИ-бухгалтером для предпринимателей, автоматизируя учет
                    и рекомендации
                  </p>
                </div>
              </div>
            </div>
            <div className="p-4 rounded-lg bg-white border border-gray-200">
              <div className="flex items-start gap-3">
                <MessageSquare className="h-5 w-5 text-purple-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Shopify Sidekick
                  </h3>
                  <p className="text-sm text-gray-600">
                    Помогает генерировать контент, сегментировать клиентов и выполнять
                    задачи прямо в админпанели магазина
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-6 rounded-xl bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200">
          <h3 className="font-semibold text-gray-900 mb-2">
            Альфа-Банк и развитие сервисов для предпринимателей
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed">
            Альфа-Банк, крупнейший частный банк в России, последовательно развивает сервисы
            для предпринимателей. Интернет-банк «Альфа-Бизнес Онлайн» и мобильное приложение
            «Альфа-Бизнес» позволяют ИП и компаниям дистанционно управлять счетами, платежами
            и документами с телефона и любых других устройств с акцентом на мобильные сценарии
            и оперативный контроль финансов. В 2024 году банк запустил «Нейроофис» — набор
            нейроассистентов для обработки документов, ответов на заявки и типовых операционных
            задач прямо внутри бизнес-банка.
          </p>
        </div>
      </div>
    </div>
  );
};

