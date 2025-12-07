import { cn } from "@/shared/lib/mergeClass";

interface CapabilityCardProps {
  title: string;
  description: string;
  imageSrc: string;
  imageAlt: string;
  videoSrc?: string;
  className?: string;
}

export const CapabilityCard = ({
  title,
  description,
  imageSrc,
  imageAlt,
  videoSrc,
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
      <div className="p-5 flex-1 bg-white rounded-4xl flex flex-col">
        <h3 className="font-bold text-lg text-[#EF3124] mb-3">{title}</h3>
        <p className="text-sm text-zinc-600 leading-relaxed mb-4">{description}</p>
        {videoSrc && (
          <div className="mt-auto rounded-xl overflow-hidden bg-gray-50 shadow-sm border border-gray-100">
            <video
              src={videoSrc}
              autoPlay
              loop
              muted
              playsInline
              className="w-full h-auto max-h-80 object-cover"
            />
          </div>
        )}
      </div>
    </div>
  );
};
