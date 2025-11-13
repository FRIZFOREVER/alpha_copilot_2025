import { OnboardingStepConfig } from "../types/onboardingTypes";

export const ONBOARDING_STEPS: OnboardingStepConfig[] = [
  {
    step: 1,
    title:
      "Расскажите немного о себе - это поможет ассистенту давать более точные и персонализированные ответы",
    placeholder: "Расскажите о себе",
    fieldName: "userInfo",
  },
  {
    step: 2,
    title:
      "Заполните информацию о своем бизнесе. Укажите сферу деятельности, основные задачи и процессы, это позволит сделать рекомендации более полезными",
    placeholder: "Опишите ваш бизнес",
    fieldName: "businessInfo",
  },
  {
    step: 3,
    title:
      "Осталось заполнить дополнительные инструкции - стиль и тон общения, приоритетные задачи, особенности бизнеса и так далее. Укажите, что считаете важным",
    placeholder: "Дополнительные инструкции",
    fieldName: "additionalInstructions",
  },
];
