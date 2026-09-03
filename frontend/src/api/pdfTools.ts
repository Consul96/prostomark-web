import { apiClient } from './http';

export interface PdfDateReplacePayload {
  file: File;
  manufactureDate: string;
  currentExpiryDate: string;
  newExpiryDate: string;
}

export interface PdfDateReplaceResult {
  blob: Blob;
  replacements: number;
  pagesChanged: number;
  pagesTotal: number;
  filename: string;
}

function filenameFromDisposition(value?: string): string {
  if (!value) return 'labels_expiry_fixed.pdf';
  const utf8 = value.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
  if (utf8) return decodeURIComponent(utf8);
  const plain = value.match(/filename="?([^";]+)"?/i)?.[1];
  return plain || 'labels_expiry_fixed.pdf';
}

export const pdfToolsApi = {
  async replaceExpiryDate(payload: PdfDateReplacePayload): Promise<PdfDateReplaceResult> {
    const form = new FormData();
    form.append('file', payload.file);
    form.append('manufacture_date', payload.manufactureDate);
    form.append('current_expiry_date', payload.currentExpiryDate);
    form.append('new_expiry_date', payload.newExpiryDate);

    const response = await apiClient.post('/pdf-tools/replace-expiry-date', form, {
      responseType: 'blob',
      timeout: 10 * 60 * 1000,
    });

    return {
      blob: response.data as Blob,
      replacements: Number(response.headers['x-prostomark-replacements'] ?? 0),
      pagesChanged: Number(response.headers['x-prostomark-pages-changed'] ?? 0),
      pagesTotal: Number(response.headers['x-prostomark-pages-total'] ?? 0),
      filename: filenameFromDisposition(response.headers['content-disposition']),
    };
  },
};
