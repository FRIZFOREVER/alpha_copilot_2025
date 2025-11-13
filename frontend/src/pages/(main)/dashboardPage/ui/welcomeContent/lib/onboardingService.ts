import {
  OnboardingStep1Data,
  OnboardingStep2Data,
  OnboardingStep3Data,
  OnboardingStep4Data,
} from "../types/onboardingTypes";

const ONBOARDING_COMPLETED_KEY = "onboarding_completed";

class OnboardingService {
  /**
   * Сохранение данных первого шага (имя пользователя)
   */
  public async saveStep1(data: OnboardingStep1Data): Promise<void> {
    // TODO: Заменить на реальный API endpoint, когда бэкенд будет готов
    // const { data: response } = await axiosAuth.post("/onboarding/step1", data);
    // return response;

    // Симуляция API вызова
    void data; // Используется в будущем для API вызова
    await new Promise((resolve) => setTimeout(resolve, 300));
  }

  /**
   * Сохранение данных второго шага (информация о пользователе)
   */
  public async saveStep2(data: OnboardingStep2Data): Promise<void> {
    // TODO: Заменить на реальный API endpoint
    // const { data: response } = await axiosAuth.post("/onboarding/step2", data);
    // return response;

    void data; // Используется в будущем для API вызова
    await new Promise((resolve) => setTimeout(resolve, 300));
  }

  /**
   * Сохранение данных третьего шага (информация о бизнесе)
   */
  public async saveStep3(data: OnboardingStep3Data): Promise<void> {
    // TODO: Заменить на реальный API endpoint
    // const { data: response } = await axiosAuth.post("/onboarding/step3", data);
    // return response;

    void data; // Используется в будущем для API вызова
    await new Promise((resolve) => setTimeout(resolve, 300));
  }

  /**
   * Сохранение данных четвертого шага (дополнительные инструкции)
   */
  public async saveStep4(data: OnboardingStep4Data): Promise<void> {
    // TODO: Заменить на реальный API endpoint
    // const { data: response } = await axiosAuth.post("/onboarding/step4", data);
    // return response;

    void data; // Используется в будущем для API вызова
    await new Promise((resolve) => setTimeout(resolve, 300));
  }

  /**
   * Отметить онбординг как завершенный
   */
  public markOnboardingCompleted(): void {
    localStorage.setItem(ONBOARDING_COMPLETED_KEY, "true");
  }

  /**
   * Проверить, завершен ли онбординг
   */
  public isOnboardingCompleted(): boolean {
    return localStorage.getItem(ONBOARDING_COMPLETED_KEY) === "true";
  }
}

export const onboardingService = new OnboardingService();
