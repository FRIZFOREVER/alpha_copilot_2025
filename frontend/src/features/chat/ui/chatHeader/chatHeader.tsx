import { useState, useEffect } from "react";
import {
  Sparkles,
  Zap,
  Brain,
  Settings,
  Minimize2,
  Maximize2,
} from "lucide-react";
import { Button } from "@/shared/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/ui/select/select";
import { useChatCollapse } from "@/shared/lib/chatCollapse";

const modelOptions = [
  {
    value: "thinking",
    label: "Fin Ai Thinking",
    description: "Думает дольше для лучших ответов",
    icon: Brain,
  },
  {
    value: "thinking-mini",
    label: "Fin Ai Thinking Mini",
    description: "Думает быстро",
    icon: Sparkles,
  },
  {
    value: "instant",
    label: "Fin Ai Instant",
    description: "Отвечает сразу",
    icon: Zap,
  },
  {
    value: "auto",
    label: "Fin Ai Auto",
    description: "Решает как долго думать",
    icon: Settings,
  },
] as const;

export const ChatHeader = () => {
  const [selectedModel, setSelectedModel] = useState<string>("thinking");
  const [isMobile, setIsMobile] = useState(false);
  const { isCollapsed, toggleCollapse } = useChatCollapse();

  const currentModel = modelOptions.find((m) => m.value === selectedModel);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);

    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  return (
    <div className="flex items-center justify-between bg-white px-4 md:px-6 py-3 border-b border-[#0d0d0d0d]">
      <div className="flex items-center justify-center flex-1 md:flex-none pl-8 md:pl-0">
        <Select value={selectedModel} onValueChange={setSelectedModel}>
          <SelectTrigger className="h-auto p-0 border-0 bg-transparent hover:bg-transparent shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 text-lg md:text-xl font-medium text-gray-900 gap-1.5 hover:text-gray-700 transition-colors cursor-pointer data-[state=open]:text-gray-700 [&>svg]:opacity-60 [&>svg]:hover:opacity-100 [&_[data-slot=select-value]]:hidden">
            <span>{currentModel?.label || "FinAi"}</span>
            <SelectValue placeholder="FinAi" />
          </SelectTrigger>
          <SelectContent
            align={isMobile ? "center" : "start"}
            alignOffset={isMobile ? undefined : -10}
            className="bg-white border-gray-200 shadow-lg min-w-[300px] p-1.5 rounded-2xl"
          >
            {modelOptions.map((model) => {
              const Icon = model.icon;
              return (
                <SelectItem
                  key={model.value}
                  value={model.value}
                  className="rounded-lg focus:bg-gray-50 focus:text-gray-900 cursor-pointer py-2.5 px-3 data-[highlighted]:bg-gray-50"
                >
                  <div className="flex items-start gap-3 w-full pr-6">
                    <Icon className="h-4 w-4 text-gray-600 flex-shrink-0 mt-0.5" />
                    <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                      <span className="font-medium text-sm text-gray-900 leading-tight">
                        {model.label}
                      </span>
                      <span className="text-xs text-gray-500 leading-tight">
                        {model.description}
                      </span>
                    </div>
                  </div>
                </SelectItem>
              );
            })}
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleCollapse}
          className="h-9 w-9 rounded-xl hover:bg-gray-100 text-gray-900 transition-all cursor-pointer"
          title={isCollapsed ? "Развернуть чат" : "Свернуть чат"}
        >
          {isCollapsed ? (
            <Maximize2 className="h-4 w-4" />
          ) : (
            <Minimize2 className="h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  );
};
