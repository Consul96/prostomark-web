import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

import { useAuthStore } from '../store/authStore';
import type { User } from './types';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 15_000,
});

const refreshClient = axios.create({
  baseURL: '/api/v1',
  timeout: 15_000,
});

let refreshingPromise: Promise<string | null> | null = null;

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalConfig = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const status = error.response?.status;

    if (status !== 401 || originalConfig._retry) {
      throw error;
    }

    const state = useAuthStore.getState();
    if (!state.refreshToken) {
      state.clearSession();
      throw error;
    }

    originalConfig._retry = true;

    if (!refreshingPromise) {
      refreshingPromise = refreshClient
        .post('/auth/refresh', { refresh_token: state.refreshToken })
        .then((response) => {
          const payload = response.data as {
            tokens: { access_token: string; refresh_token: string };
            user: User;
          };
          useAuthStore.getState().setSession(payload.tokens.access_token, payload.tokens.refresh_token, payload.user);
          return payload.tokens.access_token;
        })
        .catch(() => {
          useAuthStore.getState().clearSession();
          return null;
        })
        .finally(() => {
          refreshingPromise = null;
        });
    }

    const newAccessToken = await refreshingPromise;
    if (!newAccessToken) {
      throw error;
    }

    originalConfig.headers.Authorization = `Bearer ${newAccessToken}`;
    return apiClient.request(originalConfig);
  },
);
