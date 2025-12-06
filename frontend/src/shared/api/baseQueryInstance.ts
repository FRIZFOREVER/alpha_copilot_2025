import axios, {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
} from "axios";
import { RequestOptions } from "https";
import { deleteAccessToken, getAccessToken } from "@/entities/token";

export class AxiosClient {
  private baseQueryV1Instance: AxiosInstance;

  constructor(baseURL: string, withAuth = false) {
    const config: AxiosRequestConfig = {
      baseURL,
      withCredentials: true,
      headers: {
        "Content-Type": "application/json",
      },
    };

    this.baseQueryV1Instance = axios.create(config);

    if (withAuth) {
      this.addAuthInterceptor();
    }
  }

  private addAuthInterceptor() {
    this.baseQueryV1Instance.interceptors.request.use((config) => {
      const token = getAccessToken();
      if (config && config.headers && token) {
        config.headers["Authorization"] = `Bearer ${token}`;
      } else {
        deleteAccessToken();
      }

      if (config.data instanceof FormData) {
        delete config.headers["Content-Type"];
      }

      return config;
    });
  }

  private handleResponse<T>(response: AxiosResponse<T>): AxiosResponse<T> {
    return response;
  }

  private handleError(error: AxiosError<{ message?: string }>): never {
    const message = error.response?.data?.message || error.message || "Error";
    throw new Error(message);
  }

  public async get<T>(
    url: string,
    params: Omit<RequestOptions, "body"> = {}
  ): Promise<AxiosResponse<T>> {
    try {
      const response = await this.baseQueryV1Instance.get<T>(url, { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error as AxiosError<{ message?: string }>);
    }
  }

  public async post<T>(
    url: string,
    data?: Record<string, unknown>,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    try {
      const response = await this.baseQueryV1Instance.post<T>(
        url,
        data,
        config
      );
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error as AxiosError<{ message?: string }>);
    }
  }

  public async put<T>(
    url: string,
    data?: Record<string, unknown>,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    try {
      const response = await this.baseQueryV1Instance.put<T>(url, data, config);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error as AxiosError<{ message?: string }>);
    }
  }

  public async patch<T>(
    url: string,
    data?: Record<string, unknown>,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    try {
      const response = await this.baseQueryV1Instance.patch<T>(
        url,
        data,
        config
      );
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error as AxiosError<{ message?: string }>);
    }
  }

  public async delete<T>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    try {
      const response = await this.baseQueryV1Instance.delete<T>(url, config);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error as AxiosError<{ message?: string }>);
    }
  }
}

<<<<<<< HEAD
// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const ML_SERVICE_URL = import.meta.env.VITE_ML_SERVICE_URL;

export const axiosNoAuth = new AxiosClient("https://jabkialphacopilot-api.ru/");
export const axiosAuth = new AxiosClient("https://jabkialphacopilot-api.ru/", true);
=======
const ML_SERVICE_URL = import.meta.env.VITE_ML_SERVICE_URL;

export const axiosNoAuth = new AxiosClient("https://jabkialphacopilot-api.ru/");
export const axiosAuth = new AxiosClient(
  "https://jabkialphacopilot-api.ru/",
  true
);
>>>>>>> master
export const axiosMockML = new AxiosClient(ML_SERVICE_URL, false);
