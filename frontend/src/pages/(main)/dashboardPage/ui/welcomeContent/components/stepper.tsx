import { cn } from "@/shared/lib/mergeClass";

interface StepperProps {
  currentStep: number;
  totalSteps: number;
  onStepClick?: (step: number) => void;
  completedSteps?: number[];
  className?: string;
}

export const Stepper = ({
  currentStep,
  totalSteps,
  onStepClick,
  completedSteps = [],
  className,
}: StepperProps) => {
  const handleStepClick = (stepNumber: number) => {
    if (onStepClick) {
      const isCompleted = completedSteps.includes(stepNumber);
      const isCurrentOrPrevious = stepNumber <= currentStep;

      if (isCompleted || isCurrentOrPrevious) {
        onStepClick(stepNumber);
      }
    }
  };

  return (
    <div className={cn("flex items-center gap-2 mb-6", className)}>
      {Array.from({ length: totalSteps }, (_, index) => {
        const stepNumber = index + 1;
        const isActive = stepNumber === currentStep;
        const isCompleted = completedSteps.includes(stepNumber);
        const isClickable =
          onStepClick && (isCompleted || stepNumber <= currentStep);

        return (
          <div
            key={stepNumber}
            className={cn(
              "flex items-center",
              index < totalSteps - 1 && "flex-1"
            )}
          >
            <div className="flex items-center flex-1">
              <div
                onClick={() => isClickable && handleStepClick(stepNumber)}
                className={cn(
                  "flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium transition-colors",
                  isActive
                    ? "bg-red-500 text-white"
                    : isCompleted
                    ? "bg-red-500 text-white"
                    : "bg-transparent border-2 border-red-200 text-red-400",
                  isClickable && "cursor-pointer hover:opacity-80"
                )}
              >
                {stepNumber}
              </div>
              {index < totalSteps - 1 && (
                <div
                  className={cn(
                    "flex-1 h-1 rounded-full mx-2 transition-colors",
                    isActive || isCompleted ? "bg-red-500" : "bg-red-200"
                  )}
                />
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
