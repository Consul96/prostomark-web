import type { AxiosError } from 'axios';

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
