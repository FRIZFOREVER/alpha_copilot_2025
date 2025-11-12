import { useEffect, useRef, useState, useCallback } from "react";
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
  targetElement?: HTMLElement | null;
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
  targetElement,
}: OnboardingCardProps) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const [cardPosition, setCardPosition] = useState<{
    top?: number | string;
    left?: number | string;
    right?: number | string;
    bottom?: number | string;
    transform?: string;
  }>({});

  const updatePositions = useCallback(() => {
    // На мобильных устройствах всегда показываем карточку по центру экрана
    if (isMobile) {
      setCardPosition({
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        right: undefined,
        bottom: undefined,
      });
      // Для шага 3 все еще нужно отслеживать позицию кнопки для подсветки
      if (currentStep === 3 && targetElement) {
        const rect = targetElement.getBoundingClientRect();
        setTargetRect(rect);
      } else {
        setTargetRect(null);
      }
      return;
    }

    // На десктопе используем логику позиционирования относительно целевого элемента
    if (currentStep === 3 && targetElement) {
      const rect = targetElement.getBoundingClientRect();
      setTargetRect(rect);

      // Примерная высота карточки (будет пересчитана после первого рендера)
      const cardHeight = 280;
      const cardWidth = 320;
      const spacing = 16;
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;
      const spaceRight = window.innerWidth - rect.right;
      const spaceLeft = rect.left;

      // Определяем, где разместить карточку
      const canPlaceBelow = spaceBelow >= cardHeight + spacing;
      const canPlaceAbove = spaceAbove >= cardHeight + spacing;
      const canPlaceRight = spaceRight >= cardWidth + spacing;
      const canPlaceLeft = spaceLeft >= cardWidth + spacing;

      // На десктопе: для кнопки в правом нижнем углу размещаем карточку слева и выше
      // Приоритет: слева и выше > слева и ниже > справа и выше > справа и ниже

      // Проверяем, достаточно ли места слева
      const minLeftSpace = cardWidth + spacing * 2;
      const hasEnoughLeftSpace = spaceLeft >= minLeftSpace;

      if (hasEnoughLeftSpace && canPlaceAbove) {
        // Слева и выше (лучший вариант для кнопки в правом нижнем углу)
        const bottomPos = window.innerHeight - rect.top + spacing;
        setCardPosition({
          top: undefined,
          bottom: bottomPos,
          left: Math.max(spacing, rect.left - cardWidth - spacing),
          right: undefined,
          transform: undefined,
        });
      } else if (hasEnoughLeftSpace && !canPlaceAbove && spaceAbove > 100) {
        // Слева, но места выше мало - размещаем как можно выше, но в пределах экрана
        const topPos = Math.max(
          spacing,
          rect.top - Math.min(cardHeight, spaceAbove - spacing * 2)
        );
        setCardPosition({
          top: topPos,
          left: Math.max(spacing, rect.left - cardWidth - spacing),
          right: undefined,
          bottom: undefined,
          transform: undefined,
        });
      } else if (canPlaceLeft && canPlaceBelow) {
        // Слева и ниже (если не помещается выше)
        setCardPosition({
          top: Math.min(
            rect.bottom + spacing,
            window.innerHeight - cardHeight - spacing
          ),
          left: Math.max(spacing, rect.left - cardWidth - spacing),
          right: undefined,
          bottom: undefined,
          transform: undefined,
        });
      } else if (canPlaceRight && canPlaceAbove) {
        // Справа и выше (если слева нет места)
        setCardPosition({
          top: undefined,
          bottom: window.innerHeight - rect.top + spacing,
          right: Math.max(spacing, window.innerWidth - rect.right + spacing),
          left: undefined,
          transform: undefined,
        });
      } else {
        // Последний вариант: слева от кнопки, позиционируем так, чтобы карточка была видна
        const calculatedLeft = Math.max(
          spacing,
          Math.min(rect.left - spacing, window.innerWidth - cardWidth - spacing)
        );
        const availableVerticalSpace = Math.max(spaceAbove, spaceBelow);

        if (availableVerticalSpace >= cardHeight) {
          // Если есть достаточно места, размещаем выше
          const topPos = Math.max(spacing, rect.top - cardHeight - spacing);
          setCardPosition({
            top: topPos,
            left: calculatedLeft,
            right: undefined,
            bottom: undefined,
            transform: undefined,
          });
        } else {
          // Если места мало, размещаем так, чтобы карточка была видна на экране
          const topPos = Math.max(
            spacing,
            Math.min(
              rect.bottom + spacing,
              window.innerHeight - cardHeight - spacing
            )
          );
          setCardPosition({
            top: topPos,
            left: calculatedLeft,
            right: undefined,
            bottom: undefined,
            transform: undefined,
          });
        }
      }
    } else {
      // Для остальных шагов на десктопе центрируем по вертикали
      setTargetRect(null);
      setCardPosition({
        top: "50%",
        left: 24,
        right: 24,
        transform: "translateY(-50%)",
      });
    }
  }, [currentStep, targetElement, isMobile]);

  useEffect(() => {
    updatePositions();

    const handleResize = () => updatePositions();
    const handleScroll = () => updatePositions();

    window.addEventListener("resize", handleResize);
    window.addEventListener("scroll", handleScroll, true);

    if (targetElement) {
      const observer = new MutationObserver(updatePositions);
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ["style", "class"],
      });

      return () => {
        window.removeEventListener("resize", handleResize);
        window.removeEventListener("scroll", handleScroll, true);
        observer.disconnect();
      };
    }

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("scroll", handleScroll, true);
    };
  }, [updatePositions, targetElement]);

  const isLastStep = currentStep === totalSteps;
  const isFirstStep = currentStep === 1;
  const isHighlightingTarget = currentStep === 3 && targetElement && targetRect;

  return (
    <>
      {/* Overlay с затемнением */}
      {/* На шаге 3 делаем overlay прозрачным для кликов, чтобы кнопка чата была кликабельна */}
      <div
        className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm"
        style={{
          pointerEvents: isHighlightingTarget ? "none" : "auto",
        }}
        onClick={(e) => {
          // Разрешаем клики на кнопку чата
          if (isHighlightingTarget && targetElement) {
            const target = e.target as HTMLElement;
            if (
              targetElement.contains(target) ||
              target.closest('button[aria-label="Открыть чат"]')
            ) {
              return;
            }
          }
          // Блокируем клики вне карточки онбординга
          if (!cardRef.current?.contains(e.target as Node)) {
            e.stopPropagation();
          }
        }}
      />

      {/* Подсветка целевого элемента на шаге 3 */}
      {isHighlightingTarget && (
        <>
          {/* Рамка подсветки с эффектом пульсации */}
          <div
            className="fixed z-[102] rounded-full border-4 border-purple-500 pointer-events-none"
            style={{
              top: `${targetRect.top - 12}px`,
              left: `${targetRect.left - 12}px`,
              width: `${targetRect.width + 24}px`,
              height: `${targetRect.height + 24}px`,
              boxShadow:
                "0 0 40px rgba(147, 51, 234, 0.9), 0 0 80px rgba(147, 51, 234, 0.6), 0 0 120px rgba(147, 51, 234, 0.3)",
              animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
            }}
          />
          {/* Внутренняя подсветка */}
          <div
            className="fixed z-[102] rounded-full border-2 border-purple-300 pointer-events-none"
            style={{
              top: `${targetRect.top - 4}px`,
              left: `${targetRect.left - 4}px`,
              width: `${targetRect.width + 8}px`,
              height: `${targetRect.height + 8}px`,
              boxShadow: "inset 0 0 20px rgba(147, 51, 234, 0.5)",
            }}
          />
        </>
      )}

      {/* Карточка онбординга */}
      <div
        ref={cardRef}
        className={cn(
          "fixed z-[101] bg-white rounded-3xl shadow-2xl pointer-events-auto",
          !isMobile && "max-w-sm w-full",
          currentStep === 3 && !isMobile && "max-w-xs"
        )}
        style={{
          ...(isMobile
            ? {
                position: "fixed",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                right: "unset",
                bottom: "unset",
                width: "calc(100vw - 32px)",
                maxWidth: "calc(100vw - 32px)",
                margin: 0,
                marginLeft: 0,
                marginRight: 0,
              }
            : {
                ...cardPosition,
                maxWidth: currentStep === 3 ? "320px" : "384px",
              }),
        }}
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
              <div className="aspect-video bg-purple-100 rounded-lg flex items-center justify-center">
                <div className="text-6xl">▶️</div>
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
  const [targetElement, setTargetElement] = useState<HTMLButtonElement | null>(
    null
  );

  // Закрываем онбординг, если чат открыт
  useEffect(() => {
    if (!isCollapsed && isOnboardingActive) {
      completeOnboarding();
    }
  }, [isCollapsed, isOnboardingActive, completeOnboarding]);

  useEffect(() => {
    if (isOnboardingActive && !isOnboardingCompleted && isCollapsed) {
      setCurrentStep(1);

      const findButton = () => {
        const button = document.querySelector(
          'button[aria-label="Открыть чат"]'
        ) as HTMLButtonElement;
        if (button) {
          setTargetElement(button);
          return true;
        }
        return false;
      };

      if (!findButton()) {
        const timer = setInterval(() => {
          if (findButton()) {
            clearInterval(timer);
          }
        }, 100);

        return () => clearInterval(timer);
      }
    }
  }, [isOnboardingActive, isOnboardingCompleted, isCollapsed]);

  // Не показываем онбординг, если чат открыт или онбординг завершен
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
      targetElement={currentStep === 3 ? targetElement : null}
    />
  );
};
