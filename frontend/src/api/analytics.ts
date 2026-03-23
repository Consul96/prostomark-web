import { apiClient } from './http';
import type {
  AnalyticsNewsSummary,
  AnalyticsPhotosHistory,
  AnalyticsPhotosSummary,
  AnalyticsSystemHealth,
  AnalyticsSummary,
  AnalyticsTimeseries,
  AnalyticsUsersTop,
} from './types';

export interface AnalyticsFilters {
  period: string;
  user_id?: string;
  chat_id?: string;
  thread_id?: string;
  event?: string;
  module?: string;
  limit?: number;
  offset?: number;
}

function buildParams(filters: AnalyticsFilters) {
  const params = new URLSearchParams();
  params.set('period', filters.period);
  if (filters.user_id) params.set('user_id', filters.user_id);
  if (filters.chat_id) params.set('chat_id', filters.chat_id);
  if (filters.thread_id) params.set('thread_id', filters.thread_id);
  if (filters.event) params.set('event', filters.event);
  if (filters.module) params.set('module', filters.module);
  if (typeof filters.limit === 'number') params.set('limit', String(filters.limit));
  if (typeof filters.offset === 'number') params.set('offset', String(filters.offset));
  return params;
}

export const analyticsApi = {
  summary: async (filters: AnalyticsFilters) => {
    const { data } = await apiClient.get<AnalyticsSummary>(`/analytics/summary?${buildParams(filters).toString()}`);
    return data;
  },
  timeseries: async (filters: AnalyticsFilters) => {
    const { data } = await apiClient.get<AnalyticsTimeseries>(`/analytics/events/timeseries?${buildParams(filters).toString()}`);
    return data;
  },
  usersTop: async (filters: AnalyticsFilters) => {
    const { data } = await apiClient.get<AnalyticsUsersTop>(`/analytics/users/top?${buildParams(filters).toString()}`);
    return data;
  },
  photosSummary: async (filters: AnalyticsFilters) => {
    const { data } = await apiClient.get<AnalyticsPhotosSummary>(`/analytics/photos/summary?${buildParams(filters).toString()}`);
    return data;
  },
  photosHistory: async (filters: AnalyticsFilters) => {
    const { data } = await apiClient.get<AnalyticsPhotosHistory>(`/analytics/photos/history?${buildParams(filters).toString()}`);
    return data;
  },
  photosMismatch: async (filters: AnalyticsFilters) => {
    const { data } = await apiClient.get<AnalyticsPhotosHistory>(`/analytics/photos/mismatch?${buildParams(filters).toString()}`);
    return data;
  },
  newsSummary: async (filters: AnalyticsFilters) => {
    const { data } = await apiClient.get<AnalyticsNewsSummary>(`/analytics/news/summary?${buildParams(filters).toString()}`);
    return data;
  },
  systemHealth: async (filters: AnalyticsFilters) => {
    const { data } = await apiClient.get<AnalyticsSystemHealth>(`/analytics/system/health?${buildParams(filters).toString()}`);
    return data;
  },
  exportCsvUrl: (filters: AnalyticsFilters) => `/api/v1/analytics/export.csv?${buildParams(filters).toString()}`,
  exportXlsxUrl: (filters: AnalyticsFilters) => `/api/v1/analytics/export.xlsx?${buildParams(filters).toString()}`,
};

