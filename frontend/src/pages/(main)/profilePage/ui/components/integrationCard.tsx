import { CheckCircle2 } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";

interface IntegrationCardProps {
  name: string;
  connected: boolean;
  imageSrc: string;
  description?: string;
  category?: string;
  onClick?: () => void;
  className?: string;
}

export const IntegrationCard = ({
  name,
  connected,
  imageSrc,
  description,
  category,
  onClick,
  className,
}: IntegrationCardProps) => {
  return (
    <div
      onClick={onClick}
      className={cn(
        "relative rounded-4xl p-6 md:p-8 cursor-pointer",
        "border-2 transition-all duration-300",
        "min-h-[280px] md:min-h-[320px]",
        "overflow-hidden",
        "border-gray-200 bg-gradient-to-br from-gray-50 to-white hover:border-gray-300 hover:shadow-md",
        className
      )}
      style={{
        backgroundImage: `url(${imageSrc})`,
        backgroundPosition: "right center",
        backgroundRepeat: "no-repeat",
        backgroundSize: "auto 80%",
      }}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-white via-white/80 to-transparent pointer-events-none" />

      <div className="relative z-10 flex flex-col h-full">
        {category && (
          <div className="mb-4">
            <span className="inline-block px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-700 bg-gray-100/90 backdrop-blur-sm uppercase tracking-wide">
              {category}
            </span>
          </div>
        )}

        <div className="flex-1 flex flex-col max-w-[60%] md:max-w-[65%]">
          <h3 className="text-xl md:text-2xl font-bold text-gray-900 mb-3">
            {name}
          </h3>
          {description && (
            <p className="text-sm md:text-base text-gray-600 leading-relaxed mb-auto">
              {description}
            </p>
          )}

          <div className="mt-4 mb-4">
            {connected ? (
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-600">
                <CheckCircle2 className="h-4 w-4" />
                Подключено
              </span>
            ) : (
              <span className="text-xs text-gray-400">Не подключено</span>
            )}
          </div>

          <button
            className={cn(
              "self-start px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
              connected
                ? "bg-gray-200 text-gray-700 hover:bg-gray-300"
                : "bg-red-600 text-white hover:bg-red-700"
            )}
            onClick={(e) => {
              e.stopPropagation();
              onClick?.();
            }}
          >
            {connected ? "Настроить" : "Подключить"}
          </button>
        </div>
      </div>
    </div>
  );
};
