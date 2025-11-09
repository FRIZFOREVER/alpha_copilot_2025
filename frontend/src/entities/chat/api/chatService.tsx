import { axiosAuth } from "@/shared/api/baseQueryInstance";
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
} from "../types/types";

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
    answerId: number,
    likeDto: LikeMessageDto
  ): Promise<LikeMessageResponse> {
    const { data } = await axiosAuth.put<LikeMessageResponse>(
      `/like/${answerId}`,
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

  public async sendVoice(voiceBlob: Blob): Promise<SendVoiceResponse> {
    const formData = new FormData();
    // Append blob with .webm extension as required by backend
    // Blob type is already "audio/webm" from MediaRecorder
    formData.append("voice", voiceBlob, "voice.webm");

    // The interceptor will handle deleting Content-Type for FormData
    const { data } = await axiosAuth.post<SendVoiceResponse>(
      "/voice",
      formData as unknown as Record<string, unknown>
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
  sendVoice,
} = new ChatService();
