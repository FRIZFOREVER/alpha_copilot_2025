import { cn } from "@/shared/lib/mergeClass";

interface CapabilityCardProps {
  title: string;
  description: string;
  imageSrc: string;
  imageAlt: string;
  className?: string;
}

export const CapabilityCard = ({
  title,
  description,
  imageSrc,
  imageAlt,
  className,
}: CapabilityCardProps) => {
  return (
    <div
      className={cn(
        "flex flex-col space-y-4 rounded-4xl shadow-md overflow-hidden bg-gradient-to-b from-gray-200 to-white",
        "transition-shadow duration-200",
        className
      )}
    >
      <div className="relative w-full h-56 flex items-center justify-center overflow-hidden pt-4">
        <img
          src={imageSrc}
          alt={imageAlt}
          className="w-full h-full object-contain"
        />
      </div>
      <div className="p-5 flex-1 bg-white rounded-4xl">
        <h3 className="font-bold text-lg text-[#EF3124] mb-3">{title}</h3>
        <p className="text-sm text-zinc-600 leading-relaxed">{description}</p>
      </div>
    </div>
  );
};
