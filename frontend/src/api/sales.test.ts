import { describe, expect, it, vi, beforeEach } from "vitest";
import { orderPayload, salesApi, type OrderPayload } from "./sales";
import { apiClient } from "./http";
vi.mock("./http", () => ({
  apiClient: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
const payload: OrderPayload = {
  customer_id: "c",
  seller_id: "s",
  order_date: "2026-10-11",
  responsible_id: null,
  source: "manual",
  delivery_address: "",
  comment: "",
  basis: "Заказ",
  vat_included: true,
  revision: 3,
  items: [
    {
      product_id: "p",
      name: "Крем",
      article: "A",
      gtin: "046",
      quantity: "1.005",
      price: "10.01",
      discount: "5",
      vat_rate: null,
      unit: "шт.",
      total: "9.56",
    },
  ],
};
describe("sales API contract", () => {
  beforeEach(() => vi.clearAllMocks());
  it("sends exact decimal strings and IDs, without server-owned snapshots", () => {
    const body = orderPayload(payload);
    expect(body.items[0]).toEqual({
      product_id: "p",
      quantity: "1.005",
      price: "10.01",
      discount: "5",
      vat_rate: null,
      unit: "шт.",
      okei: "796",
    });
    expect(body.revision).toBe(3);
  });
  it("requests authoritative backend totals", async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: { total: "9.56" } });
    expect(await salesApi.calculate(payload)).toEqual({ total: "9.56" });
    expect(apiClient.post).toHaveBeenCalledWith(
      "/sales/calculate",
      orderPayload(payload),
    );
  });
  it("downloads through the authenticated client as a binary response", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: "bytes" });
    await salesApi.download("doc", "xlsx");
    expect(apiClient.get).toHaveBeenCalledWith(
      "/sales/documents/doc/download",
      { params: { format: "xlsx" }, responseType: "blob" },
    );
  });
  it("preserves the caller idempotency key on issue retries", async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: { id: "doc" } });
    const request = {
      document_type: "upd",
      idempotency_key: "stable-key",
      document_date: "2026-10-11",
    };
    await salesApi.issue("order", request);
    await salesApi.issue("order", request);
    expect(apiClient.post).toHaveBeenNthCalledWith(
      1,
      "/sales/orders/order/documents",
      request,
    );
    expect(apiClient.post).toHaveBeenNthCalledWith(
      2,
      "/sales/orders/order/documents",
      request,
    );
  });
});
