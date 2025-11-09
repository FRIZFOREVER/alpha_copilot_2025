import { useEffect, useState } from "react";
import { Image } from "@/shared/ui/image/image";
import { cn } from "@/shared/lib/mergeClass";

const WELCOME_TEXT =
  "Добро пожаловать! Я ваш AI-консультант. Задавайте разнопрофильные бизнес-вопросы, и я предоставлю вам качественные ответы на основе передовых технологий машинного обучения.";

export const ChatEmptyState = () => {
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
    <div className="flex h-full items-center justify-center px-4 md:px-8 py-12">
      <div className="flex flex-col items-center justify-center space-y-8 max-w-2xl w-full">
        <div className="relative">
          <div className="absolute inset-0 -z-10 bg-gradient-to-br from-red-500/20 to-pink-600/20 rounded-full blur-3xl animate-pulse scale-150" />
          <div
            className={cn(
              "relative transition-all duration-700 ease-out",
              imageLoaded
                ? "opacity-100 scale-100 translate-y-0"
                : "opacity-0 scale-95 translate-y-4"
            )}
          >
            <Image
              src="/images/meditation-yaga.png"
              alt="AI Consultant"
              className="w-48 md:w-64 h-auto drop-shadow-2xl select-none"
              loading="eager"
              onLoad={() => setImageLoaded(true)}
            />
          </div>
        </div>

        <div
          className={cn(
            "text-center space-y-4 transition-all duration-700 ease-out",
            imageLoaded
              ? "opacity-100 translate-y-0"
              : "opacity-0 translate-y-4"
          )}
          style={{ transitionDelay: imageLoaded ? "300ms" : "0ms" }}
        >
          <div className="bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 rounded-2xl p-6 md:p-8 shadow-xl border border-gray-200/50 dark:border-gray-700/50 backdrop-blur-sm">
            <p className="text-base md:text-lg text-gray-700 dark:text-gray-300 leading-relaxed min-h-[5rem] md:min-h-[4rem]">
              {displayedText}
              {isTyping && (
                <span className="inline-block w-0.5 h-5 md:h-6 bg-red-500 ml-1 align-middle cursor-blink" />
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
