import {
  axiosAuth,
  axiosNoAuth,
  axiosMockML,
} from "@/shared/api/baseQueryInstance";
import {
  AuthResponse,
  LoginDto,
  RegisterDto,
  ProfileResponse,
  UpdateProfileDto,
  TelegramAuthStartRequest,
  TelegramAuthStartResponse,
  TelegramAuthVerifyRequest,
  TelegramAuthVerifyResponse,
  TelegramStatusRequest,
  TelegramStatusResponse,
  TelegramContactsRequest,
  TelegramContactsResponse,
  TelegramSendMessageRequest,
  TelegramSendMessageResponse,
} from "../types/types";

class AuthService {
  public async userLogin(loginDto: LoginDto): Promise<AuthResponse> {
    const { data } = await axiosNoAuth.put<AuthResponse>("/auth", {
      ...loginDto,
    });

    return data;
  }

  public async userRegister(registerDto: RegisterDto): Promise<AuthResponse> {
    const { data } = await axiosNoAuth.post<AuthResponse>("/reg", {
      ...registerDto,
    });

    return data;
  }

  public async logout(): Promise<void> {
    await axiosAuth.delete("/auth/logout");
  }

  public async getProfile(): Promise<ProfileResponse> {
    const { data } = await axiosAuth.get<ProfileResponse>("/profile");
    return data;
  }

  public async updateProfile(
    requestDto: Partial<UpdateProfileDto>
  ): Promise<UpdateProfileDto> {
    const { data } = await axiosAuth.put<UpdateProfileDto>(
      "/profile_other_info",
      requestDto
    );
    return data;
  }

  public async getTelegramStatus(
    request: TelegramStatusRequest
  ): Promise<TelegramStatusResponse> {
    const { data } = await axiosMockML.post<TelegramStatusResponse>(
      "/telegram/user/status",
      { ...request }
    );
    return data;
  }

  public async startTelegramAuth(
    request: TelegramAuthStartRequest
  ): Promise<TelegramAuthStartResponse> {
    const { data } = await axiosMockML.post<TelegramAuthStartResponse>(
      "/telegram/user/auth/start",
      { ...request }
    );
    return data;
  }

  public async verifyTelegramAuth(
    request: TelegramAuthVerifyRequest
  ): Promise<TelegramAuthVerifyResponse> {
    const { data } = await axiosMockML.post<TelegramAuthVerifyResponse>(
      "/telegram/user/auth/verify",
      { ...request }
    );
    return data;
  }

  public async getTelegramContacts(
    request: TelegramContactsRequest
  ): Promise<TelegramContactsResponse> {
    const { data } = await axiosMockML.post<TelegramContactsResponse>(
      "/telegram/user/contacts",
      { ...request }
    );
    return data;
  }

  public async sendTelegramMessage(
    request: TelegramSendMessageRequest
  ): Promise<TelegramSendMessageResponse> {
    const { data } = await axiosMockML.post<TelegramSendMessageResponse>(
      "/telegram/user/send/message",
      { ...request }
    );
    return data;
  }
}

const authService = new AuthService();

export const {
  userLogin,
  userRegister,
  logout,
  getProfile,
  updateProfile,
  getTelegramStatus,
  startTelegramAuth,
  verifyTelegramAuth,
  sendTelegramMessage,
  getTelegramContacts,
} = authService;
