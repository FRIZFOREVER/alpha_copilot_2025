import { ELocalStorageKeys } from "@/shared/lib/storageKeys";

class TokenService {
  public setAccessToken(accessToken: string) {
    localStorage.setItem(ELocalStorageKeys.ACCESS_TOKEN_KEY, accessToken);
  }

  public deleteAccessToken() {
    localStorage.removeItem(ELocalStorageKeys.ACCESS_TOKEN_KEY);
  }

  public getAccessToken() {
    return localStorage.getItem(ELocalStorageKeys.ACCESS_TOKEN_KEY);
  }
}

export const { deleteAccessToken, getAccessToken, setAccessToken } =
  new TokenService();
