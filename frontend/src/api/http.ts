import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

import { useAuthStore } from '../store/authStore';
import { classifyApiError } from './errors';
import { recordApi } from '../shared/telemetry';
import type { User } from './types';

/**
 * 20s default timeout. Deliberately not lowered to a few seconds: on VPN/RDP a
 * genuine-but-slow request (or a file upload) must still be allowed to finish.
 * Perceived responsiveness is handled in the UI instead — a "slow" banner
 * appears after ~6s and every screen offers a manual retry (see QueryState).
 */
const DEFAULT_TIMEOUT = 20_000;

type TimedConfig = InternalAxiosRequestConfig & { metadata?: { start: number } };

export const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: DEFAULT_TIMEOUT,
});

const refreshClient = axios.create({
  baseURL: '/api/v1',
  timeout: DEFAULT_TIMEOUT,
});

/** Endpoint label for telemetry — method + path, never query/body/token. */
function endpointLabel(config?: InternalAxiosRequestConfig): string {
  const method = (config?.method ?? 'get').toUpperCase();
  const url = (config?.url ?? '').split('?')[0];
  return `${method} ${url}`;
}

let refreshingPromise: Promise<string | null> | null = null;

apiClient.interceptors.request.use((config: TimedConfig) => {
  config.metadata = { start: Date.now() };
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    const cfg = response.config as TimedConfig;
    const durationMs = cfg.metadata ? Date.now() - cfg.metadata.start : 0;
    recordApi({ label: endpointLabel(cfg), durationMs, outcome: 'ok', status: response.status });
    return response;
  },
  async (error: AxiosError) => {
    const originalConfig = error.config as TimedConfig & { _retry?: boolean };
    const status = error.response?.status;

    // Diagnostics: log slow/failed calls only (no token, no body).
    const durationMs = originalConfig?.metadata ? Date.now() - originalConfig.metadata.start : 0;
    const kind = classifyApiError(error);
    recordApi({
      label: endpointLabel(originalConfig),
      durationMs,
      outcome: kind === 'timeout' ? 'timeout' : kind === 'network' ? 'network' : 'error',
      status,
    });

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
