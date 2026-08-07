import type { AxiosError } from 'axios';

export type ApiErrorKind = 'timeout' | 'network' | 'server' | 'client' | 'unknown';

/**
 * Coarse classification used by the resilient loading UI to decide the message
 * and whether a retry is likely to help.
 */
export function classifyApiError(error: unknown): ApiErrorKind {
  const axiosError = error as AxiosError | undefined;
  if (!axiosError) return 'unknown';
  if (axiosError.code === 'ECONNABORTED' || /timeout/i.test(axiosError.message ?? '')) return 'timeout';
  const status = axiosError.response?.status;
  if (status === undefined) return 'network'; // no response reached us
  if (status >= 500) return 'server';
  if (status >= 400) return 'client';
  return 'unknown';
}

/** A retry is only worth offering for transient conditions. */
export function isRetriableError(error: unknown): boolean {
  const kind = classifyApiError(error);
  return kind === 'timeout' || kind === 'network' || kind === 'server';
}

interface ErrorResponse {
  detail?: string | { msg?: string }[] | { message?: string };
  message?: string;
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  const axiosError = error as AxiosError<ErrorResponse> | undefined;
  const data = axiosError?.response?.data;

  if (typeof data?.detail === 'string' && data.detail.trim()) {
    return data.detail;
  }

  if (Array.isArray(data?.detail) && data.detail.length > 0) {
    const firstError = data.detail[0];
    if (typeof firstError?.msg === 'string' && firstError.msg.trim()) {
      return firstError.msg;
    }
  }

  if (typeof data?.message === 'string' && data.message.trim()) {
    return data.message;
  }

  return fallback;
}
