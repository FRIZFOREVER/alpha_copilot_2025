import { useState, useEffect } from "react";
import { Stepper } from "./components/stepper";
import { StepForm } from "./components/stepForm";
import { CapabilityCard } from "./components/capabilityCard";
import { OnboardingCompleted } from "./components/onboardingCompleted";
import { ONBOARDING_STEPS } from "./lib/onboardingSteps";
import { onboardingService } from "./lib/onboardingService";
import { useUpdateProfile } from "@/entities/auth/hooks/useUpdateProfile";
import { UpdateProfileDto } from "@/entities/auth/types/types";
import { cn } from "@/shared/lib/mergeClass";

const TOTAL_STEPS = 3;

const CAPABILITIES = [
  {
    title: "Документы и письма",
    description:
      "Пишет и редактирует письма и документы, резюмирует переписку и встречи, собирает черновые презентации и таблицы.",
    imageSrc: "/images/people-maskot-4.png",
    imageAlt: "Документы и письма",
  },
  {
    title: "Экономия времени",
    description:
      "У владельцев бизнеса уходит меньше времени на операционные задачи и больше - на стратегию и работу с людьми.",
    imageSrc: "/images/people-maskot-2.png",
    imageAlt: "Экономия времени",
  },
  {
    title: "Маркетинг и аналитика",
    description:
      "Помогает с маркетингом (посты, промомеханики). Анализирует операционные данные (продажи, остатки, платежи) и рекомендует следующие шаги.",
    imageSrc: "/images/people-maskot-6.png",
    imageAlt: "Маркетинг и аналитика",
  },
  {
    title: "Юридические вопросы",
    description:
      "Отвечает на типовые юридические и финансовые вопросы, предлагает шаблоны и чек-листы.",
    imageSrc: "/images/people-maskot-3.png",
    imageAlt: "Юридические вопросы",
  },
] as const;

export const WelcomeContent = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [profileInfo, setProfileInfo] = useState<Partial<UpdateProfileDto>>({});
  const [isOnboardingCompleted, setIsOnboardingCompleted] = useState(false);

  const { mutate: updateProfileMutate } = useUpdateProfile();

  useEffect(() => {
    const completed = onboardingService.isOnboardingCompleted();
    setIsOnboardingCompleted(completed);
  }, []);

  const handleStepSubmit = async (value: string) => {
    try {
      switch (currentStep) {
        case 1: {
          setProfileInfo((prev) => ({ ...prev, user_info: value }));
          break;
        }
        case 2: {
          setProfileInfo((prev) => ({ ...prev, business_info: value }));
          break;
        }
        case 3: {
          updateProfileMutate({
            ...profileInfo,
            additional_instructions: value,
          });
          onboardingService.markOnboardingCompleted();
          setIsOnboardingCompleted(true);
          return;
        }
      }

      setCompletedSteps((prev) => {
        if (!prev.includes(currentStep)) {
          return [...prev, currentStep];
        }
        return prev;
      });

      if (currentStep < TOTAL_STEPS) {
        setCurrentStep(currentStep + 1);
      }
    } catch (error) {
      console.error("Ошибка при сохранении данных шага:", error);
    }
  };

  const handleStepBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleStepClick = (step: number) => {
    if (completedSteps.includes(step) || step <= currentStep) {
      setCurrentStep(step);
    }
  };

  const currentStepConfig = ONBOARDING_STEPS[currentStep - 1];
  const canGoBack = currentStep > 1;

  return (
    <div className="h-full overflow-y-auto scrollbar-hide">
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-4 md:py-6">
        <div className="mb-8 md:mb-16">
          <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-4 md:mb-6">
            Бизнес-контекст
          </h2>
          <div
            className={cn(
              "p-4 md:p-6 lg:p-10 rounded-3xl md:rounded-4xl bg-white shadow-sm"
            )}
          >
            {isOnboardingCompleted ? (
              <OnboardingCompleted />
            ) : (
              <>
                <Stepper
                  currentStep={currentStep}
                  totalSteps={TOTAL_STEPS}
                  onStepClick={handleStepClick}
                  completedSteps={completedSteps}
                />
                <StepForm
                  stepConfig={currentStepConfig}
                  initialValue=""
                  onSubmit={handleStepSubmit}
                  onBack={handleStepBack}
                  canGoBack={canGoBack}
                />
              </>
            )}
          </div>
        </div>
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-4 md:mb-6">
            Возможности
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
            {CAPABILITIES.map((capability) => (
              <CapabilityCard
                key={capability.title}
                title={capability.title}
                description={capability.description}
                imageSrc={capability.imageSrc}
                imageAlt={capability.imageAlt}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
