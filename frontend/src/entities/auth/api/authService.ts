import { Profile } from "@/entities/profile/types/types";
import { axiosAuth, axiosNoAuth } from "@/shared/api/baseQueryInstance";
import { LoginDto, RegisterDto } from "../types/types";

class AuthService {
  public async adminLogin(loginDto: LoginDto): Promise<Profile> {
    const { data } = await axiosNoAuth.post<Profile>("/admin/auth/login", {
      ...loginDto,
    });

    return data;
  }

  public async userLogin(loginDto: LoginDto): Promise<Profile> {
    const { data } = await axiosNoAuth.post<Profile>("/auth/login", {
      ...loginDto,
    });

    return data;
  }

  public async userRegister(registerDto: RegisterDto): Promise<Profile> {
    const { data } = await axiosNoAuth.post<Profile>("/auth/register", {
      ...registerDto,
    });

    return data;
  }

  public async refresh(): Promise<string> {
    const { data } = await axiosNoAuth.post<string>("/auth/refresh");

    return data;
  }

  public async logout(): Promise<void> {
    await axiosAuth.delete("/auth/logout");
  }
}

export const { adminLogin, userLogin, userRegister, refresh, logout } =
  new AuthService();
