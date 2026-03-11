import { apiClient } from './http';
import type { DashboardSummary } from './types';

export const dashboardApi = {
  summary: async () => {
    const { data } = await apiClient.get<DashboardSummary>('/dashboard/summary');
    return data;
  },
};
