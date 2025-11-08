import { EProfileRoles } from "@/entities/profile/types/types";

export interface AuthSlice {
  selectRole: EProfileRoles | null;
}
