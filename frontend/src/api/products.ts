import { apiClient } from './http';
import type { Product } from './types';

export interface ProductPayload {
  name: string;
  brand?: string;
  gtin?: string;
  article?: string;
}

export const productsApi = {
  list: async () => {
    const { data } = await apiClient.get<Product[]>('/products');
    return data;
  },
  create: async (payload: ProductPayload) => {
    const { data } = await apiClient.post<Product>('/products', payload);
    return data;
  },
  update: async (id: string, payload: ProductPayload) => {
    const { data } = await apiClient.put<Product>(`/products/${id}`, payload);
    return data;
  },
  remove: async (id: string) => {
    await apiClient.delete(`/products/${id}`);
  },
};
