import { cn } from "@/shared/lib/mergeClass";
import { Image } from "@/shared/ui/image/image";
import { Variants, motion } from "framer-motion";
import { PropsWithChildren } from "react";

export const sectionVariants: Variants = {
  hidden: { opacity: 0, y: 50 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut", staggerChildren: 0.2 },
  },
};

export const AuthWrapper = ({ children }: PropsWithChildren) => {
  return (
    <motion.section
      className="flex justify-center"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.3 }}
      variants={sectionVariants}
      whileHover="hover"
    >
      <div
        className={cn(
          "w-full h-full md:w-[1070px] md:h-[608px] flex-col flex bg-lilac-100 rounded-4xl md:flex-row bg-white",
        )}
      >
        <div className="w-full md:py-0 p-8 flex items-center justify-center bg-gradient-to-br from-[#ef3124]/80 to-pink-600/80 rounded-4xl">
          <Image
            src={"/images/4.png"}
            alt="logo"
            className="w-[200px] md:w-[250px] select-none"
          />
        </div>
        {children}
      </div>
    </motion.section>
  );
};
