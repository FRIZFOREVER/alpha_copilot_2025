import { useState, useEffect, useRef } from "react";
import { Button } from "@/shared/ui";
import { cn } from "@/shared/lib/mergeClass";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { OnboardingStepConfig } from "../types/onboardingTypes";

interface StepFormProps {
  stepConfig: OnboardingStepConfig;
  initialValue?: string;
  onSubmit: (value: string) => Promise<void>;
  onBack?: () => void;
  canGoBack: boolean;
  className?: string;
}

export const StepForm = ({
  stepConfig,
  initialValue = "",
  onSubmit,
  onBack,
  canGoBack,
  className,
}: StepFormProps) => {
  const [value, setValue] = useState(initialValue);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setValue(initialValue);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [initialValue, stepConfig.step]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit(value.trim());
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBack = () => {
    if (canGoBack && onBack) {
      onBack();
    }
  };

  return (
    <form onSubmit={handleSubmit} className={cn("space-y-4", className)}>
      <div>
        <label
          htmlFor={`step-${stepConfig.step}-textarea`}
          className="block text-sm md:text-base text-gray-900 mb-3 font-medium"
        >
          {stepConfig.title}
        </label>
        <div className="flex gap-3 md:gap-4 flex-col">
          <div className="relative">
            <textarea
              ref={textareaRef}
              id={`step-${stepConfig.step}-textarea`}
              value={value}
              placeholder={stepConfig.placeholder}
              onChange={handleChange}
              disabled={isSubmitting}
              rows={4}
              className={cn(
                "w-full resize-none",
                "px-4 py-3 md:px-5 md:py-4",
                "text-sm md:text-base text-gray-900",
                "bg-white rounded-xl md:rounded-3xl",
                "border border-[#f0f3f7]",
                "shadow-sm",
                "placeholder:text-gray-400",
                "focus:outline-none focus:ring-1 focus:ring-red-500 focus:border-red-500",
                "transition-all duration-200",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "min-h-[20px] md:min-h-[80px]",
                "max-h-[60px] md:max-h-[100px] overflow-y-auto"
              )}
            />
          </div>
          <div className="flex items-center justify-center gap-3 md:gap-4">
            {canGoBack && (
              <Button
                type="button"
                onClick={handleBack}
                disabled={isSubmitting}
                className={cn(
                  "h-10 w-10 md:h-11 md:w-11",
                  "rounded-full cursor-pointer",
                  "bg-gradient-to-r from-red-500 to-pink-600",
                  "hover:from-red-600 hover:to-pink-700",
                  "text-white font-medium",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  "transition-all duration-200",
                  "flex items-center justify-center"
                )}
              >
                <ChevronLeft className="w-5 h-5 md:w-6 md:h-6" />
              </Button>
            )}
            <Button
              type="submit"
              disabled={!value.trim() || isSubmitting}
              className={cn(
                "h-10 w-10 md:h-11 md:w-11",
                "rounded-full cursor-pointer",
                "bg-gradient-to-r from-red-500 to-pink-600",
                "hover:from-red-600 hover:to-pink-700",
                "text-white font-medium",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "transition-all duration-200",
                "flex items-center justify-center"
              )}
            >
              <ChevronRight className="w-5 h-5 md:w-6 md:h-6" />
            </Button>
          </div>
        </div>
      </div>
    </form>
  );
};
