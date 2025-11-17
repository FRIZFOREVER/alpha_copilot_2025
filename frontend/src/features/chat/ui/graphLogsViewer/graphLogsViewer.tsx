import { useState, useEffect, useMemo } from "react";
import { X, FileText } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { useGraphLogsQuery } from "@/entities/chat/hooks/useGraphLogs";
import { useGraphLogEvents } from "@/shared/hooks/useGraphLogEvents";
import {
  GraphLog,
  GraphLogWebSocketMessage,
} from "@/entities/chat/types/types";
import { ScrollArea } from "@/shared/ui/scroll-area";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
} from "@/shared/ui/drawer/drawer";
import { useResize } from "@/shared/hooks/useResize";
import { GraphLogCard } from "./graphLogCard";

interface GraphLogsViewerProps {
  answerId: number;
  isOpen: boolean;
  onClose: () => void;
}

export const GraphLogsViewer = ({
  answerId,
  isOpen,
  onClose,
}: GraphLogsViewerProps) => {
  const [realtimeLogs, setRealtimeLogs] = useState<GraphLogWebSocketMessage[]>(
    []
  );

  const { isLgView } = useResize();
  const { data: initialLogs, isLoading } = useGraphLogsQuery(
    isOpen ? answerId : undefined
  );

  useGraphLogEvents((message: GraphLogWebSocketMessage) => {
    if (message.answer_id === answerId) {
      setRealtimeLogs((prev) => [...prev, message]);
    }
  });

  const allLogs = useMemo(() => {
    const initial: GraphLog[] = initialLogs || [];
    const realtime: GraphLog[] = realtimeLogs.map((log, index) => ({
      id: initial.length + index + 1,
      tag: log.tag,
      message: log.message,
      log_time: new Date().toISOString(),
      answer_id: log.answer_id,
    }));

    return [...initial, ...realtime];
  }, [initialLogs, realtimeLogs]);

  useEffect(() => {
    if (!isOpen) {
      setRealtimeLogs([]);
    }
  }, [isOpen]);

  useEffect(() => {
    setRealtimeLogs([]);
  }, [answerId]);

  return (
    <>
      <div
        className={cn(
          "bg-white border-l border-[#0000000f] flex-shrink-0 transition-all duration-300 ease-in-out md:flex hidden flex-col h-full overflow-hidden",
          isOpen ? "w-96 opacity-100" : "w-0 opacity-0"
        )}
      >
        {isOpen && (
          <div className="flex flex-col h-full w-full">
            <div className="flex items-center justify-between p-[14.2px] border-b border-[#0000000f]">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-gray-900">
                  Активность
                </h2>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-md hover:bg-gray-100 transition-colors"
                aria-label="Закрыть"
              >
                <X className="h-5 w-5 text-gray-600" />
              </button>
            </div>

            <ScrollArea className="flex-1 p-4">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <p className="text-sm text-gray-500">Загрузка логов...</p>
                </div>
              ) : allLogs.length === 0 ? (
                <div className="flex items-center justify-center py-8">
                  <p className="text-sm text-gray-500">Логи отсутствуют</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {[...allLogs].reverse().map((log, index) => (
                    <GraphLogCard
                      key={`${log.id}-${index}`}
                      log={log}
                      index={index}
                    />
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>
        )}
      </div>
      {isOpen && isLgView && (
        <div className="md:hidden">
          <Drawer open={isOpen} onOpenChange={onClose}>
            <DrawerContent className="max-h-[80vh]">
              <DrawerHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-gray-600" />
                    <DrawerTitle>Graph Logs</DrawerTitle>
                  </div>
                </div>
                <DrawerDescription>
                  Логи выполнения для ответа #{answerId}
                </DrawerDescription>
              </DrawerHeader>

              <ScrollArea className="flex-1 p-4">
                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <p className="text-sm text-gray-500">Загрузка логов...</p>
                  </div>
                ) : allLogs.length === 0 ? (
                  <div className="flex items-center justify-center py-8">
                    <p className="text-sm text-gray-500">Логи отсутствуют</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {[...allLogs].reverse().map((log, index) => (
                      <GraphLogCard
                        key={`${log.id}-${index}`}
                        log={log}
                        index={index}
                      />
                    ))}
                  </div>
                )}
              </ScrollArea>
            </DrawerContent>
          </Drawer>
        </div>
      )}
    </>
  );
};
