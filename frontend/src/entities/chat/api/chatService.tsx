import { axiosAuth } from "@/shared/api/baseQueryInstance";
import { getAccessToken } from "@/entities/token";
import {
  CreateChatDto,
  CreateChatResponse,
  GetChatsResponse,
  GetHistoryResponse,
  LikeMessageDto,
  LikeMessageResponse,
  SendMessageDto,
  SendMessageResponse,
  SendVoiceResponse,
  UploadFileResponse,
  SendMessageStreamDto,
  SendMessageStreamCallbacks,
  StreamInitialResponse,
  StreamChunk,
  SearchMessagesResponse,
} from "../types/types";

const API_BASE_URL = "http://127.0.0.1:8080";

class ChatService {
  public async createChat(
    createChatDto: CreateChatDto
  ): Promise<CreateChatResponse> {
    const { data } = await axiosAuth.post<CreateChatResponse>("/chat", {
      ...createChatDto,
    });

    return data;
  }

  public async getChats(): Promise<GetChatsResponse> {
    const { data } = await axiosAuth.get<GetChatsResponse>("/chats");

    return data;
  }

  public async getHistory(chatId: number): Promise<GetHistoryResponse> {
    const { data } = await axiosAuth.get<GetHistoryResponse>(
      `/history/${chatId}`
    );

    return data;
  }

  public async likeMessage(
    chatId: number,
    likeDto: LikeMessageDto
  ): Promise<LikeMessageResponse> {
    const { data } = await axiosAuth.put<LikeMessageResponse>(
      `/like/${chatId}`,
      likeDto as unknown as Record<string, unknown>
    );

    return data;
  }

  public async sendMessage(
    chatId: number,
    sendMessageDto: SendMessageDto
  ): Promise<SendMessageResponse> {
    const { data } = await axiosAuth.post<SendMessageResponse>(
      `/message/${chatId}`,
      sendMessageDto as unknown as Record<string, unknown>
    );

    return data;
  }

  public async sendMessageStream(
    chatId: number,
    sendMessageDto: SendMessageStreamDto,
    callbacks: SendMessageStreamCallbacks
  ): Promise<void> {
    const token = getAccessToken();

    if (!token) {
      callbacks.onError?.(new Error("Токен авторизации не найден"));
      return;
    }

    try {
      const baseURL = API_BASE_URL.endsWith("/")
        ? API_BASE_URL.slice(0, -1)
        : API_BASE_URL;
      const url = `${baseURL}/message_stream/${chatId}`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          question: sendMessageDto.question,
          voice_url: sendMessageDto.voice_url || "",
          file_url: sendMessageDto.file_url || "",
          tag: sendMessageDto.tag || "",
          mode: sendMessageDto.mode || "",
          send_to_telegram: sendMessageDto.send_to_telegram || false,
          phone_number: sendMessageDto.phone_number || "",
          recipient_id: sendMessageDto.recipient_id || "",
        }),
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => "Unknown error");
        throw new Error(
          `HTTP error! status: ${response.status}, message: ${errorText}`
        );
      }

      if (!response.body) {
        throw new Error("Response body is null");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let isInitialReceived = false;

      const processSSEEvent = (data: string): boolean => {
        if (!data.trim()) return false;

        try {
          const json = JSON.parse(data);
          console.log(json);
          if (!isInitialReceived) {
            const initialData = json as StreamInitialResponse;
            callbacks.onInitial?.(initialData);
            isInitialReceived = true;
            return false;
          } else {
            const chunk = json as StreamChunk;
            callbacks.onChunk?.(chunk);

            if (chunk.done) {
              callbacks.onComplete?.();
              return true;
            }
            return false;
          }
        } catch (error) {
          console.error("Ошибка при парсинге JSON:", error, data);
          return false;
        }
      };

      const processBuffer = (): boolean => {
        let eventEndIndex: number;

        while ((eventEndIndex = buffer.indexOf("\n\n")) !== -1) {
          const eventData = buffer.substring(0, eventEndIndex);
          buffer = buffer.substring(eventEndIndex + 2);

          const lines = eventData.split("\n");
          let jsonData: string | null = null;

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed) continue;

            if (trimmed.startsWith("data: ")) {
              jsonData = trimmed.substring(6).trim();
              break;
            }

            if (trimmed.startsWith("{")) {
              jsonData = trimmed;
              break;
            }
          }

          if (jsonData) {
            const shouldStop = processSSEEvent(jsonData);
            if (shouldStop) {
              return true;
            }
          }
        }

        return false;
      };

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        const shouldStop = processBuffer();
        if (shouldStop) {
          return;
        }
      }

      if (buffer.trim()) {
        const lines = buffer.split("\n");
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          if (trimmed.startsWith("data: ")) {
            const jsonData = trimmed.substring(6).trim();
            const shouldStop = processSSEEvent(jsonData);
            if (shouldStop) {
              return;
            }
            break;
          }

          if (trimmed.startsWith("{")) {
            const shouldStop = processSSEEvent(trimmed);
            if (shouldStop) {
              return;
            }
            break;
          }
        }
      }

      if (!isInitialReceived) {
        callbacks.onError?.(new Error("Начальный ответ не был получен"));
        return;
      }

      callbacks.onComplete?.();
    } catch (error) {
      callbacks.onError?.(
        error instanceof Error ? error : new Error(String(error))
      );
    }
  }

  public async sendVoice(voiceBlob: Blob): Promise<SendVoiceResponse> {
    const formData = new FormData();
    formData.append("voice", voiceBlob, "voice.webm");

    const { data } = await axiosAuth.post<SendVoiceResponse>(
      "/voice",
      formData as unknown as Record<string, unknown>
    );

    return data;
  }

  public async uploadFile(file: File): Promise<UploadFileResponse> {
    const formData = new FormData();
    formData.append("file", file, file.name);

    const { data } = await axiosAuth.post<UploadFileResponse>(
      "/file",
      formData as unknown as Record<string, unknown>
    );

    return data;
  }

  public async searchMessages(
    pattern: string
  ): Promise<SearchMessagesResponse> {
    // Форматируем паттерн для SQL LIKE: добавляем % вокруг текста для поиска в любом месте
    const likePattern = `%${pattern}%`;
    const encodedPattern = encodeURIComponent(likePattern);
    const { data } = await axiosAuth.get<SearchMessagesResponse>(
      `/search?pattern=${encodedPattern}`
    );

    return data;
  }
}

export const {
  createChat,
  getChats,
  getHistory,
  likeMessage,
  sendMessage,
  sendMessageStream,
  sendVoice,
  uploadFile,
  searchMessages,
} = new ChatService();
