import { useEffect, useRef, useState } from "react";
import { useOnboarding } from "@/shared/lib/onboarding";
import { Button } from "@/shared/ui/button";
import { cn } from "@/shared/lib/mergeClass";
import { useResize } from "@/shared/hooks/useResize";
import { X, Check } from "lucide-react";
import { Progress } from "@/shared/ui/progress/progress";
import { useChatCollapse } from "@/shared/lib/chatCollapse";

interface OnboardingStep {
  id: number;
  title: string;
  description: string;
  emoji: string;
  content?: React.ReactNode;
}

const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 1,
    title: "Welcome!",
    description:
      "Добро пожаловать в приложение-помощник для малого бизнеса. Мы поможем вам автоматизировать ключевые задачи и экономить время.",
    emoji: "👋",
  },
  {
    id: 2,
    title: "Get started",
    description:
      "Начните использовать возможности ИИ-помощника прямо сейчас. Выполните несколько простых шагов, чтобы начать.",
    emoji: "👆",
  },
  {
    id: 3,
    title: "Discover your Dashboard",
    description:
      "Познакомьтесь с вашей панелью управления. Обратите внимание на кнопку помощника в правом нижнем углу — это ваш ключевой инструмент для работы с ИИ.",
    emoji: "📊",
  },
  {
    id: 4,
    title: "Watch guide",
    description:
      "Посмотрите краткое руководство, чтобы узнать больше о возможностях вашего ИИ-помощника.",
    emoji: "▶️",
  },
];

interface OnboardingCardProps {
  step: OnboardingStep;
  currentStep: number;
  totalSteps: number;
  progress: number;
  onNext: () => void;
  onPrevious: () => void;
  onSkip: () => void;
  isMobile: boolean;
}

const OnboardingCard = ({
  step,
  currentStep,
  totalSteps,
  progress,
  onNext,
  onPrevious,
  onSkip,
  isMobile,
}: OnboardingCardProps) => {
  const cardRef = useRef<HTMLDivElement>(null);

  const isLastStep = currentStep === totalSteps;
  const isFirstStep = currentStep === 1;

  return (
    <>
      <div
        className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm"
        onClick={(e) => {
          if (!cardRef.current?.contains(e.target as Node)) {
            e.stopPropagation();
          }
        }}
      />

      <div
        ref={cardRef}
        className={cn(
          "fixed z-[101] bg-white rounded-3xl shadow-2xl pointer-events-auto",
          "top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2",
          isMobile
            ? "w-[calc(100vw-32px)] max-w-[calc(100vw-32px)]"
            : "max-w-sm w-full",
          currentStep === 3 && !isMobile && "max-w-xs"
        )}
      >
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="text-4xl mb-3">{step.emoji}</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {step.title}
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {step.description}
              </p>
            </div>
            <button
              onClick={onSkip}
              className="ml-4 text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
              aria-label="Пропустить онбординг"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {currentStep === 2 && (
            <div className="mb-4 space-y-3">
              <Progress value={progress} className="h-2" />
              <div className="space-y-2">
                {[
                  { id: 1, label: "Создать первый чат", completed: true },
                  { id: 2, label: "Настроить профиль", completed: false },
                  { id: 3, label: "Изучить возможности", completed: false },
                ].map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center gap-2 text-sm text-gray-600"
                  >
                    <div
                      className={cn(
                        "w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0",
                        task.completed
                          ? "bg-purple-500 text-white"
                          : "border-2 border-gray-300"
                      )}
                    >
                      {task.completed && <Check className="h-3 w-3" />}
                    </div>
                    <span
                      className={cn(
                        task.completed && "line-through text-gray-400"
                      )}
                    >
                      {task.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="mb-4">
              <div className="aspect-video bg-black rounded-lg overflow-hidden">
                <video
                  className="w-full h-full object-contain"
                  controls
                  autoPlay
                  muted
                  loop
                  playsInline
                >
                  <source
                    src="https://getfile.dokpub.com/yandex/get/https://disk.yandex.ru/i/YPOS7y_jAnQbqQ"
                    type="video/mp4"
                  />
                  Ваш браузер не поддерживает видео.
                </video>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">
                Краткое руководство по использованию
              </p>
            </div>
          )}

          {currentStep === 3 && (
            <div className="mb-4 flex gap-1 justify-center">
              {Array.from({ length: totalSteps }).map((_, idx) => (
                <div
                  key={idx}
                  className={cn(
                    "h-2 rounded-full transition-all duration-300",
                    idx + 1 === currentStep
                      ? "w-6 bg-purple-500"
                      : "w-2 bg-gray-300"
                  )}
                />
              ))}
            </div>
          )}

          <div className="flex items-center justify-between gap-2 mt-6">
            {!isFirstStep && (
              <Button
                variant="outline"
                onClick={onPrevious}
                className="flex-1 rounded-2xl cursor-pointer"
              >
                Назад
              </Button>
            )}
            <Button
              onClick={isLastStep ? onSkip : onNext}
              className={cn(
                "flex-1 rounded-2xl cursor-pointer",
                isFirstStep && "w-full"
              )}
            >
              {isLastStep
                ? "Завершить"
                : currentStep === 1
                ? "Продолжить"
                : "Далее"}
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};

export const Onboarding = () => {
  const {
    isOnboardingActive,
    isOnboardingCompleted,
    completeOnboarding,
    skipOnboarding,
  } = useOnboarding();
  const { isCollapsed } = useChatCollapse();
  const [currentStep, setCurrentStep] = useState(1);
  const { isMobileView } = useResize();

  useEffect(() => {
    if (isOnboardingActive && !isOnboardingCompleted) {
      setCurrentStep(1);
    }
  }, [isOnboardingActive, isOnboardingCompleted]);

  useEffect(() => {
    if (!isCollapsed && isOnboardingActive) {
      completeOnboarding();
    }
  }, [isCollapsed, isOnboardingActive, completeOnboarding]);

  if (!isOnboardingActive || isOnboardingCompleted || !isCollapsed) {
    return null;
  }

  const currentStepData = ONBOARDING_STEPS[currentStep - 1];
  const progress = (currentStep / ONBOARDING_STEPS.length) * 100;

  const handleNext = () => {
    if (currentStep < ONBOARDING_STEPS.length) {
      setCurrentStep(currentStep + 1);
    } else {
      completeOnboarding();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    skipOnboarding();
  };

  return (
    <OnboardingCard
      step={currentStepData}
      currentStep={currentStep}
      totalSteps={ONBOARDING_STEPS.length}
      progress={progress}
      onNext={handleNext}
      onPrevious={handlePrevious}
      onSkip={handleSkip}
      isMobile={isMobileView}
    />
  );
};
