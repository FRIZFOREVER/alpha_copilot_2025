import { cn } from "@/shared/lib/mergeClass";

interface SourcesButtonProps {
  count: number;
  onClick: () => void;
  className?: string;
}

export const SourcesButton = ({
  count,
  onClick,
  className,
}: SourcesButtonProps) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 px-3 py-1.5 rounded-full",
        "bg-white border border-gray-200",
        "hover:bg-gray-50 hover:border-gray-300 transition-colors",
        "cursor-pointer shadow-sm",
        className
      )}
      aria-label={`Показать ${count} источников`}
      title={`Показать ${count} источников`}
    >
      <div className="flex items-center -space-x-2 flex-shrink-0">
        {/* Первая иконка - черный круг с треугольником вверх */}
        <div className="relative w-5 h-5 rounded-full bg-black flex items-center justify-center z-10 border border-white">
          <svg
            width="6"
            height="6"
            viewBox="0 0 8 8"
            fill="none"
            className="text-white"
          >
            <path d="M4 2L6 6H2L4 2Z" fill="white" />
          </svg>
        </div>
        {/* Вторая иконка - черный круг с треугольником вверх */}
        <div className="relative w-5 h-5 rounded-full bg-black flex items-center justify-center z-20 border border-white">
          <svg
            width="6"
            height="6"
            viewBox="0 0 8 8"
            fill="none"
            className="text-white"
          >
            <path d="M4 2L6 6H2L4 2Z" fill="white" />
          </svg>
        </div>
        {/* Третья иконка - красный круг с треугольником вправо (play) */}
        <div className="relative w-5 h-5 rounded-full bg-red-500 flex items-center justify-center z-30 border border-white">
          <svg
            width="5"
            height="5"
            viewBox="0 0 6 6"
            fill="none"
            className="text-white"
          >
            <path d="M2 1L5 3L2 5V1Z" fill="white" />
          </svg>
        </div>
      </div>
      <span className="text-xs font-medium text-gray-900 whitespace-nowrap">
        {count} ИСТОЧНИКОВ
      </span>
    </button>
  );
};
