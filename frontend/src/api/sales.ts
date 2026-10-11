import { apiClient } from "./http";
import type { Product } from "./types";
export type Kind = "person" | "ip" | "legal";
export type Source = "telegram" | "vk" | "phone" | "other" | "manual";
export type DocType = "torg12" | "upd" | "invoice";
export type Details = Record<string, string | string[] | null>;
export interface Customer {
  id: string;
  kind: Kind;
  name: string;
  phone: string | null;
  inn: string | null;
  details: Details;
  archived: boolean;
  responsible_id: string;
  orders_count: number;
  last_order: string | null;
  duplicates: { id: string; name: string }[];
}
export interface VatRule {
  from_date: string;
  to_date: string | null;
  rates: (string | null)[];
}
export interface Seller {
  id: string;
  kind: "ip" | "legal";
  name: string;
  inn: string | null;
  details: Details;
  active: boolean;
  vat_rules: VatRule[];
}
export interface Line {
  product_id: string;
  name?: string;
  article?: string | null;
  gtin?: string | null;
  unit: string;
  okei?: string;
  quantity: string;
  price: string;
  discount: string;
  vat_rate: string | null;
  total?: string;
  vat_amount?: string;
}
export interface OrderPayload {
  customer_id: string;
  seller_id: string;
  responsible_id: string | null;
  order_date: string;
  source: Source;
  delivery_address: string;
  comment: string;
  basis: string;
  vat_included: boolean;
  items: Line[];
  revision?: number;
}
export interface Order extends OrderPayload {
  id: string;
  number: string;
  customer_name: string;
  seller_name: string;
  responsible_name: string;
  status: "draft" | "confirmed" | "completed" | "cancelled";
  total: string;
  vat_total: string;
  discount_total: string;
}
export interface SalesDocument {
  id: string;
  order_id: string;
  seller_id: string;
  document_type: DocType;
  number: number;
  year: number;
  document_date: string;
  version: number;
  order_revision: number;
}
export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}
export interface Template {
  id: string;
  document_type: DocType;
  name: string;
  version: number;
}
export interface HistoryEvent {
  id: string;
  action: string;
  created_at: string;
  user_id: string;
  meta_json: Record<string, unknown>;
}
export interface Totals {
  total: string;
  vat_total: string;
  discount_total: string;
  lines: { total: string; vat_amount: string }[];
}
export const sourceLabels: Record<Source, string> = {
  telegram: "Telegram",
  vk: "ВКонтакте",
  phone: "Телефон",
  other: "Другой канал",
  manual: "Ручной ввод",
};
export const statusLabels = {
  draft: "Черновик",
  confirmed: "Подтверждён",
  completed: "Завершён вручную",
  cancelled: "Отменён",
};
export const kindLabels = {
  person: "Физическое лицо",
  ip: "ИП",
  legal: "Юридическое лицо",
};
export const docLabels: Record<DocType, string> = {
  torg12: "ТОРГ-12",
  upd: "УПД",
  invoice: "Товарная накладная",
};
export function orderPayload(order: OrderPayload): OrderPayload {
  return {
    customer_id: order.customer_id,
    seller_id: order.seller_id,
    responsible_id: order.responsible_id,
    order_date: order.order_date,
    source: order.source,
    delivery_address: order.delivery_address,
    comment: order.comment,
    basis: order.basis,
    vat_included: order.vat_included,
    revision: order.revision,
    items: order.items.map(
      ({ product_id, unit, okei, quantity, price, discount, vat_rate }) => ({
        product_id,
        unit,
        okei: okei || "796",
        quantity,
        price,
        discount,
        vat_rate,
      }),
    ),
  };
}
export const salesApi = {
  list: async <T>(resource: string, params: Record<string, unknown> = {}) =>
    (await apiClient.get<Page<T>>(`/sales/${resource}`, { params })).data,
  get: async <T>(resource: string, id: string) =>
    (await apiClient.get<T>(`/sales/${resource}/${id}`)).data,
  save: async <T>(resource: string, payload: unknown, id?: string) =>
    (id
      ? await apiClient.patch<T>(`/sales/${resource}/${id}`, payload)
      : await apiClient.post<T>(`/sales/${resource}`, payload)
    ).data,
  action: async (id: string, action: string) =>
    (await apiClient.post<Order>(`/sales/orders/${id}/${action}`)).data,
  catalog: async (q: string) =>
    (await apiClient.get<Page<Product>>("/sales/catalog", { params: { q } }))
      .data,
  staff: async () =>
    (await apiClient.get<{ id: string; name: string }[]>("/sales/staff")).data,
  templates: async () =>
    (await apiClient.get<Template[]>("/sales/templates")).data,
  history: async (id: string) =>
    (await apiClient.get<HistoryEvent[]>(`/sales/orders/${id}/history`)).data,
  calculate: async (order: OrderPayload) =>
    (await apiClient.post<Totals>("/sales/calculate", orderPayload(order)))
      .data,
  issue: async (id: string, payload: unknown) =>
    (
      await apiClient.post<SalesDocument>(
        `/sales/orders/${id}/documents`,
        payload,
      )
    ).data,
  preview: async (id: string, payload: unknown) =>
    (
      await apiClient.post<Blob>(
        `/sales/orders/${id}/documents/preview`,
        payload,
        { responseType: "blob" },
      )
    ).data,
  download: async (id: string, format: "xlsx" | "pdf") =>
    (
      await apiClient.get<Blob>(`/sales/documents/${id}/download`, {
        params: { format },
        responseType: "blob",
      })
    ).data,
};
export function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}
