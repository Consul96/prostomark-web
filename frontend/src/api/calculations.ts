import { apiClient } from './http';
import type { Calculation } from './types';

export const calculationsApi = {
  list: async () => {
    const { data } = await apiClient.get<Calculation[]>('/calculations');
    return data;
  },
  create: async (input_json: Record<string, unknown>, currency = 'RUB') => {
    const { data } = await apiClient.post<Calculation>('/calculations', {
      input_json,
      currency,
    });
    return data;
  },
};
