import { Share2, Copy, MoreVertical } from "lucide-react";
import { Button } from "@/shared/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export const ChatHeader = () => {
  return (
    <div className="flex items-center justify-between border-b border-gray-200/50 bg-white px-4 md:px-6 py-3">
      <div className="flex items-center gap-4">
        <h2 className="text-lg md:text-xl font-semibold text-gray-900">
          AI <span className="text-red-500">Copilot</span>
        </h2>
        <Select defaultValue="thinking">
          <SelectTrigger className="w-[240px] h-9 text-sm rounded-xl border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300 text-gray-900 shadow-sm hover:shadow transition-all focus-visible:ring-2 focus-visible:ring-blue-500/20 focus-visible:border-blue-500">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-white border-gray-200 rounded-xl shadow-lg">
            <SelectItem
              value="auto"
              className="rounded-lg focus:bg-gray-100 focus:text-gray-900 cursor-pointer"
            >
              Auto - Решает как долго думать
            </SelectItem>
            <SelectItem
              value="instant"
              className="rounded-lg focus:bg-gray-100 focus:text-gray-900 cursor-pointer"
            >
              Instant - Отвечает сразу
            </SelectItem>
            <SelectItem
              value="thinking-mini"
              className="rounded-lg focus:bg-gray-100 focus:text-gray-900 cursor-pointer"
            >
              Thinking mini - Думает быстро
            </SelectItem>
            <SelectItem
              value="thinking"
              className="rounded-lg focus:bg-gray-100 focus:text-gray-900 cursor-pointer"
            >
              Thinking - Думает дольше для лучших ответов
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 rounded-xl hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition-all"
        >
          <Share2 className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 rounded-xl hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition-all"
        >
          <Copy className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 rounded-xl hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition-all"
        >
          <MoreVertical className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};
