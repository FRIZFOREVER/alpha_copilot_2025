import { axiosAuth, axiosNoAuth } from "@/shared/api/baseQueryInstance";
import {
  AuthResponse,
  LoginDto,
  RegisterDto,
  ProfileResponse,
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
}

export const { userLogin, userRegister, logout, getProfile } =
  new AuthService();
