import { EProfileRoles } from "@/entities/profile/types/types";

export interface LoginDto {
  email: string;
  password: string;
}

export interface RegisterDto {
  full_name: string;
  email: string;
  password: string;
  role: EProfileRoles;
  company_id?: number;
  university_id?: number;
}
