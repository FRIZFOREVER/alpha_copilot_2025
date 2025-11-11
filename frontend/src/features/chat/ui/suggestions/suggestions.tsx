import { useState, useRef, useEffect } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { Button } from "@/shared/ui/button";

export interface Suggestion {
  id: string;
  title: string;
  subtitle: string;
}

interface SuggestionsProps {
  suggestions: Suggestion[];
  onSelect: (suggestion: Suggestion) => void;
  className?: string;
}

export const Suggestions = ({
  suggestions,
  onSelect,
  className,
}: SuggestionsProps) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  if (!suggestions || suggestions.length === 0) return null;

  const shouldShowArrows = suggestions.length > 3;

  const checkScrollability = () => {
    if (!scrollContainerRef.current) return;

    const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
    setCanScrollLeft(scrollLeft > 0);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
  };

  useEffect(() => {
    checkScrollability();
    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener("scroll", checkScrollability);
      window.addEventListener("resize", checkScrollability);
      return () => {
        container.removeEventListener("scroll", checkScrollability);
        window.removeEventListener("resize", checkScrollability);
      };
    }
  }, [suggestions]);

  const scroll = (direction: "left" | "right") => {
    if (!scrollContainerRef.current) return;

    const container = scrollContainerRef.current;
    const scrollAmount = 320;
    const targetScroll =
      direction === "left"
        ? container.scrollLeft - scrollAmount
        : container.scrollLeft + scrollAmount;

    container.scrollTo({
      left: targetScroll,
      behavior: "smooth",
    });
  };

  return (
    <div
      className={cn(
        "relative px-0",
        className,
        !shouldShowArrows && "flex justify-center"
      )}
    >
      {shouldShowArrows && canScrollLeft && (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => scroll("left")}
          className={cn(
            "absolute left-0 top-1/2 cursor-pointer -translate-y-1/2 z-10",
            "h-8 w-8 rounded-full",
            "bg-white/90 backdrop-blur-sm",
            "border border-gray-200 shadow-md",
            "hover:bg-white hover:shadow-lg",
            "transition-all duration-200",
            "hidden md:flex"
          )}
        >
          <ChevronLeft className="h-4 w-4 text-gray-700" />
        </Button>
      )}

      <div ref={scrollContainerRef} className="overflow-x-auto scrollbar-hide ">
        <div className="flex gap-3 min-w-max pb-2">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.id}
              onClick={() => onSelect(suggestion)}
              className={cn(
                "px-4 py-3 rounded-2xl cursor-pointer",
                "bg-gray-100 hover:bg-gray-200 active:bg-gray-200",
                "border border-gray-200",
                "text-left transition-all duration-200",
                "active:scale-[0.98]",
                "min-w-[200px] max-w-[280px]",
                "flex-shrink-0"
              )}
            >
              <div className="font-semibold text-gray-900 text-sm mb-1">
                {suggestion.title}
              </div>
              <div className="text-xs text-gray-600 leading-relaxed">
                {suggestion.subtitle}
              </div>
            </button>
          ))}
        </div>
      </div>

      {shouldShowArrows && canScrollRight && (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => scroll("right")}
          className={cn(
            "absolute right-0 cursor-pointer top-1/2 -translate-y-1/2 z-10",
            "h-8 w-8 rounded-full",
            "bg-white/90 backdrop-blur-sm",
            "border border-gray-200 shadow-md",
            "hover:bg-white hover:shadow-lg",
            "transition-all duration-200",
            "hidden md:flex"
          )}
        >
          <ChevronRight className="h-4 w-4 text-gray-700" />
        </Button>
      )}
    </div>
  );
};
