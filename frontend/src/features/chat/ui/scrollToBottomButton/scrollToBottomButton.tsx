import { memo } from "react";
import { ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/shared/lib/mergeClass";

export interface ScrollToBottomButtonProps {
  show: boolean;
  onClick: () => void;
}

export const ScrollToBottomButton = memo(
  ({ show, onClick }: ScrollToBottomButtonProps) => {
    return (
      <AnimatePresence>
        {show && (
          <motion.button
            onClick={onClick}
            initial={{ opacity: 0, scale: 0, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0, y: 20 }}
            whileHover={{ scale: 1.1, y: -2 }}
            whileTap={{ scale: 0.95 }}
            transition={{
              type: "spring",
              stiffness: 400,
              damping: 25,
            }}
            className={cn(
              "absolute bottom-4 right-4 md:right-8 z-10 md:hidden",
              "w-10 h-10 rounded-full",
              "bg-gradient-to-br from-white to-gray-50",
              "border-2 border-gray-200",
              "text-gray-700 shadow-xl",
              "flex items-center justify-center",
              "backdrop-blur-sm",
              "hover:border-gray-300",
              "hover:shadow-2xl",
              "focus:outline-none",
              "transition-colors duration-200",
              "cursor-pointer"
            )}
            aria-label="Прокрутить вниз"
          >
            <motion.div
              animate={{
                y: [0, 3, 0],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              <ChevronDown className="w-5 h-5" strokeWidth={2.5} />
            </motion.div>
          </motion.button>
        )}
      </AnimatePresence>
    );
  }
);

ScrollToBottomButton.displayName = "ScrollToBottomButton";
