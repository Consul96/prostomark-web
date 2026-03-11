import { apiClient } from './http';
import type { Document } from './types';

export interface UploadDocumentPayload {
  file: File;
  product_id?: string;
  document_type?: string;
  number?: string;
  document_date?: string;
}

export const documentsApi = {
  list: async () => {
    const { data } = await apiClient.get<Document[]>('/documents');
    return data;
  },
  upload: async (payload: UploadDocumentPayload) => {
    const formData = new FormData();
    formData.append('file', payload.file);
    if (payload.product_id) formData.append('product_id', payload.product_id);
    if (payload.document_type) formData.append('document_type', payload.document_type);
    if (payload.number) formData.append('number', payload.number);
    if (payload.document_date) formData.append('document_date', payload.document_date);

    const { data } = await apiClient.post<Document>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
  remove: async (id: string) => {
    await apiClient.delete(`/documents/${id}`);
  },
};
