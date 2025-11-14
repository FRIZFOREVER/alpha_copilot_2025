import { useState, useRef } from "react";
import { cn } from "@/shared/lib/mergeClass";

export interface Suggestion {
  id: string;
  title: string;
  subtitle: string;
}

interface SuggestionsProps {
  suggestions: Suggestion[];
  onSelect: (suggestion: Suggestion) => void;
  className?: string;
  isCompact?: boolean;
}

export const Suggestions = ({
  suggestions,
  onSelect,
  className,
}: SuggestionsProps) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [hasDragged, setHasDragged] = useState(false);

  if (!suggestions || suggestions.length === 0) return null;

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!scrollContainerRef.current) return;
    setIsDragging(true);
    setHasDragged(false);
    setStartX(e.pageX - scrollContainerRef.current.offsetLeft);
    setScrollLeft(scrollContainerRef.current.scrollLeft);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !scrollContainerRef.current) return;
    e.preventDefault();
    const x = e.pageX - scrollContainerRef.current.offsetLeft;
    const walk = (x - startX) * 2;
    scrollContainerRef.current.scrollLeft = scrollLeft - walk;
    if (Math.abs(walk) > 5) {
      setHasDragged(true);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setTimeout(() => setHasDragged(false), 100);
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
    setTimeout(() => setHasDragged(false), 100);
  };

  const handleSuggestionClick = (
    e: React.MouseEvent,
    suggestion: Suggestion,
  ) => {
    if (hasDragged) {
      e.preventDefault();
      return;
    }
    onSelect(suggestion);
  };
  return (
    <div className={cn("relative flex justify-center", className)}>
      <div
        ref={scrollContainerRef}
        className={cn(
          "overflow-x-auto scrollbar-hide",
          "cursor-grab active:cursor-grabbing",
          "select-none",
        )}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
      >
        <div className="flex gap-3 min-w-max pb-2">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.id}
              onClick={(e) => handleSuggestionClick(e, suggestion)}
              className={cn(
                "px-4 py-2.5 rounded-2xl cursor-pointer",
                "bg-gray-100 hover:bg-gray-200 active:bg-gray-200",
                "border border-gray-200",
                "text-left transition-all duration-200",
                "active:scale-[0.98]",
                "min-w-[200px] max-w-[280px]",
                "flex-shrink-0",
              )}
            >
              <div className="font-semibold text-gray-900 text-sm">
                {suggestion.title}
              </div>
              <div className="text-xs text-gray-600 leading-relaxed">
                {suggestion.subtitle}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
