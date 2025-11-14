import { cn } from "@/shared/lib/mergeClass";
import { Image } from "@/shared/ui/image/image";

interface OnboardingCompletedProps {
  className?: string;
}

export const OnboardingCompleted = ({
  className,
}: OnboardingCompletedProps) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center px-6 py-6",
        className
      )}
    >
      <div className="mb-6">
        <Image
          src={"/images/heart-1.webp"}
          alt="blimfy-logo"
          width={100}
          height={100}
          className="w-[100px] hover:scale-105 transition-transform duration-300 cursor-pointer"
        />
      </div>
      <h3 className="text-xl md:text-2xl text-gray-900 mb-3 text-center">
        Форма заполнена
      </h3>
      <p className="text-lg text-gray-600 text-center leading-2">Спасибо!</p>
    </div>
  );
};
