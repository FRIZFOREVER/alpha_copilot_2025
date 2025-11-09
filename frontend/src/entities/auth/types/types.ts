export interface LoginDto {
  login: string;
  password: string;
}

export interface RegisterDto {
  login: string;
  username: string;
  password: string;
}

export interface AuthResponse {
  jwt: string;
}

export interface ProfileResponse {
  id: number;
  login: string;
  username: string;
}
