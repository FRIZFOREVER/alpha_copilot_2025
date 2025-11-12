import { motion } from "framer-motion";

export const TypingIndicator = () => {
  return (
    <div className="flex items-center gap-2 py-3 pl-1">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2.5 h-2.5 rounded-full"
          animate={{
            backgroundColor: ["#60A5FA", "#34D399", "#FBBF24", "#60A5FA"],
            scale: [1, 1.4, 1],
            opacity: [0.6, 1, 0.6],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * 0.3,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
};
