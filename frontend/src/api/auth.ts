import { apiClient } from './http';
import type { AuthResponse, User } from './types';

export interface RegisterPayload {
  company_name: string;
  company_slug?: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authApi = {
  register: async (payload: RegisterPayload) => {
    const { data } = await apiClient.post<AuthResponse>('/auth/register', payload);
    return data;
  },
  login: async (payload: LoginPayload) => {
    const { data } = await apiClient.post<AuthResponse>('/auth/login', payload);
    return data;
  },
  logout: async (refreshToken: string) => {
    await apiClient.post('/auth/logout', { refresh_token: refreshToken });
  },
  me: async () => {
    const { data } = await apiClient.get<User>('/auth/me');
    return data;
  },
};
