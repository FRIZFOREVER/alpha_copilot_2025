import { useState, useRef, useEffect } from "react";
import { Play, Pause, ChevronUp } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { axiosAuth } from "@/shared/api/baseQueryInstance";

export interface VoiceMessageProps {
  voiceUrl: string;
  transcription?: string;
  className?: string;
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
};

// Генерация простой визуализации волны с фиксированным паттерном
const generateWaveform = (bars: number = 20, progress: number = 0): number[] => {
  const waveform: number[] = [];
  const progressBar = Math.floor(progress * bars);
  
  // Фиксированный паттерн для более естественного вида
  const pattern = [0.3, 0.6, 0.4, 0.8, 0.5, 0.7, 0.4, 0.9, 0.6, 0.5, 0.7, 0.4, 0.6, 0.8, 0.5, 0.7, 0.4, 0.6, 0.5, 0.8];
  
  for (let i = 0; i < bars; i++) {
    const baseHeight = pattern[i % pattern.length] || 0.5;
    
    if (i < progressBar) {
      // Активные бары (уже проигранные) - более яркие и высокие
      waveform.push(baseHeight * 0.9 + 0.1);
    } else if (i === progressBar && progress > 0) {
      // Текущий бар - немного выше для визуального эффекта
      waveform.push(baseHeight * 1.1);
    } else {
      // Неактивные бары - ниже
      waveform.push(baseHeight * 0.6 + 0.2);
    }
  }
  return waveform;
};

const getVoiceFileNameFromUrl = (url: string): string => {
  const parts = url.split("/");
  return parts[parts.length - 1] || "voice.webm";
};

const getVoiceFileUrl = (voiceUrl: string): string => {
  if (voiceUrl.startsWith("http")) {
    return voiceUrl;
  }
  
  const fileName = getVoiceFileNameFromUrl(voiceUrl);
  return `/voices/${fileName}`;
};

export const VoiceMessage = ({
  voiceUrl,
  transcription,
  className,
}: VoiceMessageProps) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const blobUrlRef = useRef<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [showTranscription, setShowTranscription] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [waveform, setWaveform] = useState<number[]>(() => generateWaveform(20, 0));
  const waveformIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const audioUrl = getVoiceFileUrl(voiceUrl);

  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
    }

    const audio = audioRef.current;

    const updateTime = () => {
      setCurrentTime(audio.currentTime);
      // Обновляем waveform при воспроизведении
      if (duration > 0) {
        const progress = audio.currentTime / duration;
        setWaveform(generateWaveform(20, progress));
      }
    };
    const updateDuration = () => {
      setDuration(audio.duration || 0);
      setIsLoading(false);
    };
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };
    const handleError = () => {
      setError("Не удалось загрузить аудио");
      setIsLoading(false);
    };
    const handleLoadedData = () => {
      setDuration(audio.duration || 0);
      setIsLoading(false);
    };

    audio.addEventListener("timeupdate", updateTime);
    audio.addEventListener("loadedmetadata", updateDuration);
    audio.addEventListener("loadeddata", handleLoadedData);
    audio.addEventListener("ended", handleEnded);
    audio.addEventListener("error", handleError);

    return () => {
      audio.removeEventListener("timeupdate", updateTime);
      audio.removeEventListener("loadedmetadata", updateDuration);
      audio.removeEventListener("loadeddata", handleLoadedData);
      audio.removeEventListener("ended", handleEnded);
      audio.removeEventListener("error", handleError);
      audio.pause();
      audio.src = "";
      if (blobUrlRef.current) {
        URL.revokeObjectURL(blobUrlRef.current);
        blobUrlRef.current = null;
      }
      if (waveformIntervalRef.current) {
        clearInterval(waveformIntervalRef.current);
        waveformIntervalRef.current = null;
      }
    };
  }, [audioUrl]);

  // Обновление waveform при изменении воспроизведения
  useEffect(() => {
    if (isPlaying && duration > 0) {
      waveformIntervalRef.current = setInterval(() => {
        if (audioRef.current) {
          const progress = audioRef.current.currentTime / duration;
          setWaveform(generateWaveform(20, progress));
        }
      }, 100); // Обновляем каждые 100мс для плавности
    } else {
      if (waveformIntervalRef.current) {
        clearInterval(waveformIntervalRef.current);
        waveformIntervalRef.current = null;
      }
    }

    return () => {
      if (waveformIntervalRef.current) {
        clearInterval(waveformIntervalRef.current);
      }
    };
  }, [isPlaying, duration]);

  const loadAudioMetadata = async () => {
    if (!audioRef.current) return;

    try {
      setIsLoading(true);
      setError(null);

      // Если аудио уже загружено, ничего не делаем
      if (audioRef.current.src && audioRef.current.readyState > 0) {
        setIsLoading(false);
        return;
      }

      // Если URL полный (http/https), используем напрямую
      if (audioUrl.startsWith("http")) {
        audioRef.current.src = audioUrl;
        audioRef.current.load();
        return;
      }

      // Для относительных путей загружаем через axios с авторизацией
      // Получаем базовый экземпляр axios для прямого доступа
      const axiosInstance = (axiosAuth as any).baseQueryV1Instance;
      
      const response = await axiosInstance.get(audioUrl, {
        responseType: "blob",
      });

      // Освобождаем предыдущий blob URL если есть
      if (blobUrlRef.current) {
        URL.revokeObjectURL(blobUrlRef.current);
      }

      const blob = response.data as Blob;
      const blobUrl = URL.createObjectURL(blob);
      blobUrlRef.current = blobUrl;
      
      if (audioRef.current) {
        audioRef.current.src = blobUrl;
        audioRef.current.load();
      }
    } catch (err) {
      console.error("Ошибка загрузки аудио:", err);
      setError("Не удалось загрузить аудио");
      setIsLoading(false);
    }
  };

  const togglePlay = async () => {
    if (!audioRef.current) return;

    try {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        // Если аудио еще не загружено, загружаем
        if (!audioRef.current.src || audioRef.current.readyState === 0) {
          await loadAudioMetadata();
        }
        await audioRef.current.play();
        setIsPlaying(true);
        setError(null);
      }
    } catch (err) {
      console.error("Ошибка воспроизведения:", err);
      setError("Не удалось воспроизвести аудио");
      setIsPlaying(false);
    }
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
  const hasTranscription = transcription && transcription.trim();

  return (
    <div className={cn("flex flex-col", className)}>
      <div
        className={cn(
          "flex flex-col rounded-2xl overflow-hidden",
          "bg-red-50 dark:bg-gray-900/60",
          "border border-red-200/50 dark:border-purple-900/40",
          "hover:bg-red-100/80 dark:hover:bg-gray-800/80",
          "transition-colors",
          "max-w-fit",
          showTranscription && hasTranscription && "pb-2",
          "shadow-sm"
        )}
      >
        {/* Основная строка с плеером */}
        <div className="flex items-center gap-2 px-3 py-2.5">
          <button
            onClick={togglePlay}
            disabled={isLoading || !!error}
            className={cn(
              "flex-shrink-0 w-10 h-10 rounded-full",
              "bg-gradient-to-br from-red-500 to-red-600",
              "hover:from-red-600 hover:to-red-700",
              "dark:from-red-600 dark:to-purple-700",
              "dark:hover:from-red-700 dark:hover:to-purple-800",
              "text-white transition-all",
              "flex items-center justify-center",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "active:scale-95",
              "shadow-md"
            )}
            aria-label={isPlaying ? "Пауза" : "Воспроизвести"}
          >
            {isLoading ? (
              <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : isPlaying ? (
              <Pause className="h-4 w-4" fill="currentColor" />
            ) : (
              <Play className="h-4 w-4 ml-0.5" fill="currentColor" />
            )}
          </button>

          {/* Визуализация волны */}
          <div className="flex items-center gap-0.5 h-6 min-w-[100px] justify-center flex-1">
            {waveform.map((height, index) => {
              const progressBar = Math.floor(progress / 5);
              const isActive = index < progressBar;
              const isCurrent = index === progressBar && isPlaying;
              
              return (
                <div
                  key={index}
                  className={cn(
                    "w-[2.5px] rounded-full transition-all duration-300 ease-out",
                    isCurrent
                      ? "bg-red-600 dark:bg-red-400 animate-pulse"
                      : isActive
                      ? "bg-red-600/90 dark:bg-red-400/90"
                      : "bg-red-400/50 dark:bg-red-500/40"
                  )}
                  style={{
                    height: `${Math.max(height * 24, 6)}px`,
                    transitionDelay: `${index * 10}ms`,
                  }}
                />
              );
            })}
          </div>

          {/* Время */}
          <div className="flex items-center gap-1 text-xs font-medium text-red-700 dark:text-red-300 min-w-[50px]">
            <span>{formatTime(currentTime)}</span>
            {duration > 0 && (
              <>
                <span className="text-red-500/60">/</span>
                <span className="text-red-500/80">{formatTime(duration)}</span>
              </>
            )}
          </div>

          {/* Кнопка раскрытия расшифровки */}
          {hasTranscription && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowTranscription(!showTranscription);
              }}
              className={cn(
                "flex-shrink-0 w-7 h-7 rounded-md",
                "bg-red-200/70 dark:bg-purple-900/50",
                "hover:bg-red-300/90 dark:hover:bg-purple-800/70",
                "text-red-700 dark:text-purple-200",
                "flex items-center justify-center",
                "transition-all",
                "active:scale-95",
                "border border-red-300/30 dark:border-purple-700/30",
                showTranscription && "bg-red-300/90 dark:bg-purple-800/70"
              )}
              aria-label={showTranscription ? "Скрыть расшифровку" : "Показать расшифровку"}
            >
              <ChevronUp
                className={cn(
                  "h-3.5 w-3.5 transition-transform duration-200",
                  !showTranscription && "rotate-180"
                )}
              />
            </button>
          )}
        </div>

        {/* Расшифровка внутри того же блока */}
        {showTranscription && hasTranscription && (
          <div className="px-3 pt-2 border-t border-red-200/50 dark:border-purple-800/40 bg-red-100/30 dark:bg-black/20">
            <p className="text-xs text-red-900/90 dark:text-gray-200/90 leading-relaxed whitespace-pre-wrap">
              {transcription}
            </p>
          </div>
        )}

        {error && (
          <div className="px-3 py-1.5 border-t border-red-200/50 dark:border-red-900/50">
            <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

