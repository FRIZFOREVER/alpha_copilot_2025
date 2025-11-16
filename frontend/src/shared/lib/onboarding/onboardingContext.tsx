import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { ELocalStorageKeys } from "@/shared/lib/storageKeys";

interface OnboardingContextType {
  isOnboardingCompleted: boolean;
  isOnboardingActive: boolean;
  startOnboarding: () => void;
  completeOnboarding: () => void;
  skipOnboarding: () => void;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(
  undefined
);

export const useOnboarding = () => {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error("useOnboarding must be used within OnboardingProvider");
  }
  return context;
};

interface OnboardingProviderProps {
  children: ReactNode;
}

export const OnboardingProvider = ({ children }: OnboardingProviderProps) => {
  const [isOnboardingCompleted, setIsOnboardingCompleted] = useState(() => {
    if (typeof window === "undefined") return false;
    const completed = localStorage.getItem(
      ELocalStorageKeys.ONBOARDING_COMPLETED
    );
    return completed === "true";
  });
  const [isOnboardingActive, setIsOnboardingActive] = useState(false);

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === ELocalStorageKeys.ONBOARDING_COMPLETED) {
        setIsOnboardingCompleted(e.newValue === "true");
        if (e.newValue === "true") {
          setIsOnboardingActive(false);
        }
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const startOnboarding = () => {
    setIsOnboardingActive(true);
  };

  const completeOnboarding = () => {
    setIsOnboardingCompleted(true);
    setIsOnboardingActive(false);
    localStorage.setItem(ELocalStorageKeys.ONBOARDING_COMPLETED, "true");
  };

  const skipOnboarding = () => {
    setIsOnboardingCompleted(true);
    setIsOnboardingActive(false);
    localStorage.setItem(ELocalStorageKeys.ONBOARDING_COMPLETED, "true");
  };

  return (
    <OnboardingContext.Provider
      value={{
        isOnboardingCompleted,
        isOnboardingActive,
        startOnboarding,
        completeOnboarding,
        skipOnboarding,
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
};
