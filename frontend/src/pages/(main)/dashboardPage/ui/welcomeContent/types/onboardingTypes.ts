export interface OnboardingStep1Data {
  userName: string;
}

export interface OnboardingStep2Data {
  userInfo: string;
}

export interface OnboardingStep3Data {
  businessInfo: string;
}

export interface OnboardingStep4Data {
  additionalInstructions: string;
}

export type OnboardingData =
  | OnboardingStep1Data
  | OnboardingStep2Data
  | OnboardingStep3Data
  | OnboardingStep4Data;

export interface OnboardingStepConfig {
  step: number;
  title: string;
  placeholder: string;
  fieldName: keyof OnboardingStep1Data | keyof OnboardingStep2Data | keyof OnboardingStep3Data | keyof OnboardingStep4Data;
  description?: string;
}

