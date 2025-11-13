import { useEffect, useState } from "react";
import { Image } from "@/shared/ui/image/image";
import { cn } from "@/shared/lib/mergeClass";

const WELCOME_TEXT =
  "Задавайте любые бизнес-вопросы — получите точный ответ за секунды.";

export const ChatEmptyState = ({
  isCompact = false,
}: {
  isCompact?: boolean;
}) => {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const [imageLoaded, setImageLoaded] = useState(false);

  useEffect(() => {
    if (!imageLoaded) return;

    let currentIndex = 0;
    let timeoutId: NodeJS.Timeout;
    const typingSpeed = 30;

    const typeText = () => {
      if (currentIndex < WELCOME_TEXT.length) {
        setDisplayedText(WELCOME_TEXT.slice(0, currentIndex + 1));
        currentIndex++;
        timeoutId = setTimeout(typeText, typingSpeed);
      } else {
        setIsTyping(false);
      }
    };

    const startTimer = setTimeout(typeText, 500);

    return () => {
      clearTimeout(startTimer);
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [imageLoaded]);

  return (
    <div
      className={cn(
        "flex items-center justify-center px-3 sm:px-4 md:px-8 py-6 sm:py-8 md:py-12 w-full",
        isCompact && "px-3 py-6 md:px-3 md:py-6"
      )}
    >
      <div
        className={cn(
          "flex flex-col items-center justify-center space-y-4 sm:space-y-6 md:space-y-8 max-w-2xl w-full",
          isCompact && "space-y-4 md:space-y-4"
        )}
      >
        <div className="relative">
          <div className="absolute inset-0 -z-10 bg-gradient-to-br from-red-500/20 to-pink-600/20 rounded-full blur-3xl animate-pulse scale-125 sm:scale-150" />
          <div
            className={cn(
              "relative transition-all duration-700 ease-out",
              imageLoaded
                ? "opacity-100 scale-100 translate-y-0"
                : "opacity-0 scale-95 translate-y-4"
            )}
          >
            <Image
              src="/images/2026.png"
              alt="AI Consultant"
              className={cn(
                "w-32 sm:w-40 md:w-48 lg:w-64 h-auto drop-shadow-2xl select-none",
                isCompact && "w-24 sm:w-32 md:w-40 lg:w-48"
              )}
              loading="eager"
              onLoad={() => setImageLoaded(true)}
            />
          </div>
        </div>

        <div
          className={cn(
            "text-center transition-opacity duration-700 ease-out px-2 sm:px-4",
            imageLoaded ? "opacity-100" : "opacity-0"
          )}
        >
          <p
            className={cn(
              "text-base sm:text-lg md:text-xl lg:text-2xl font-medium text-gray-800 leading-relaxed",
              isCompact && "text-base sm:text-base md:text-base lg:text-base"
            )}
          >
            {displayedText}
            {isTyping && (
              <span className="inline-block w-0.5 sm:w-1 h-4 sm:h-5 md:h-6 bg-red-500 ml-1 align-middle cursor-blink" />
            )}
          </p>
        </div>
      </div>
    </div>
  );
};
