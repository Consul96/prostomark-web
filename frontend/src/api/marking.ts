import { apiClient } from './http';

// ------------------------- Типы -------------------------

export interface CrptClient {
  id: string;
  company_id: string;
  name: string;
  inn: string;
  environment: string;
  product_groups: string[];
  oms_id: string | null;
  oms_connection: string | null;
  timezone: string;
  signer_agent_id: string | null;
  signer_certificate_thumbprint: string | null;
  is_active: boolean;
  true_api_status: string;
  suz_status: string;
  mchd_status: string;
  mchd_number: string | null;
  mchd_valid_from: string | null;
  mchd_valid_until: string | null;
  last_connection_check_at: string | null;
  settings: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CrptClientCreate {
  name: string;
  inn: string;
  environment?: string;
  product_groups?: string[];
  oms_id?: string | null;
  oms_connection?: string | null;
  timezone?: string;
  signer_agent_id?: string | null;
  mchd_number?: string | null;
  mchd_valid_from?: string | null;
  mchd_valid_until?: string | null;
}

export interface ConnectionCheckResult {
  mchd_status: string;
  true_api_status: string;
  suz_status: string;
}

export interface MarkingApplication {
  id: string;
  crpt_client_id: string;
  external_application_number: string | null;
  title: string;
  product_group: string;
  workflow_type: string | null;
  release_method: string | null;
  status: string;
  progress: Record<string, unknown>;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
}

export interface MarkingApplicationCreate {
  crpt_client_id: string;
  title: string;
  product_group: string;
  external_application_number?: string | null;
  workflow_type?: string | null;
  release_method?: string | null;
}

export interface MarkingDashboard {
  active_applications: number;
  cards_with_errors: number;
  gtin_pending_publication: number;
  km_orders_processing: number;
  km_ready_to_receive: number;
  application_report_mismatches: number;
  circulation_pending_signature: number;
  circulation_rejected: number;
  mchd_expiring: number;
  sign_agents_unavailable: number;
  attention: Array<{ type: string; count: number; message: string }>;
}

export interface SignerAgent {
  id: string;
  name: string;
  certificate_thumbprint: string | null;
  is_active: boolean;
  last_heartbeat_at: string | null;
  version: string | null;
  created_at: string;
}

export interface SignerAgentCreated extends SignerAgent {
  api_key: string;
}

export interface MarkingOperationLog {
  id: string;
  crpt_client_id: string | null;
  application_id: string | null;
  client_inn: string | null;
  operation: string;
  object_type: string | null;
  object_id: string | null;
  rows_or_km_count: number | null;
  result: string;
  external_id: string | null;
  correlation_id: string | null;
  error_message: string | null;
  created_at: string;
}

// ------------------------- API -------------------------

export const markingApi = {
  dashboard: () => apiClient.get<MarkingDashboard>('/marking/dashboard').then((r) => r.data),

  listClients: () => apiClient.get<CrptClient[]>('/marking/clients').then((r) => r.data),
  createClient: (payload: CrptClientCreate) =>
    apiClient.post<CrptClient>('/marking/clients', payload).then((r) => r.data),
  getClient: (id: string) => apiClient.get<CrptClient>(`/marking/clients/${id}`).then((r) => r.data),
  updateClient: (id: string, payload: Partial<CrptClientCreate> & { is_active?: boolean }) =>
    apiClient.patch<CrptClient>(`/marking/clients/${id}`, payload).then((r) => r.data),
  deactivateClient: (id: string) =>
    apiClient.post<CrptClient>(`/marking/clients/${id}/deactivate`).then((r) => r.data),
  checkConnection: (id: string) =>
    apiClient.post<ConnectionCheckResult>(`/marking/clients/${id}/check-connection`).then((r) => r.data),

  listApplications: () =>
    apiClient.get<MarkingApplication[]>('/marking/applications').then((r) => r.data),
  createApplication: (payload: MarkingApplicationCreate) =>
    apiClient.post<MarkingApplication>('/marking/applications', payload).then((r) => r.data),
  getApplication: (id: string) =>
    apiClient.get<MarkingApplication>(`/marking/applications/${id}`).then((r) => r.data),

  listAgents: () => apiClient.get<SignerAgent[]>('/marking/sign-agent/agents').then((r) => r.data),
  createAgent: (payload: { name: string; certificate_thumbprint?: string }) =>
    apiClient.post<SignerAgentCreated>('/marking/sign-agent/agents', payload).then((r) => r.data),

  history: () => apiClient.get<MarkingOperationLog[]>('/marking/history').then((r) => r.data),
};

export const PRODUCT_GROUPS: Array<{ code: string; title: string }> = [
  { code: 'lp', title: 'Лёгкая промышленность' },
  { code: 'shoes', title: 'Обувь' },
];

export const CONNECTION_STATUS_LABELS: Record<string, string> = {
  ok: 'Подключено',
  needs_setup: 'Требуется настройка',
  expired: 'МЧД истекла',
  cert_unavailable: 'Сертификат недоступен',
  unavailable: 'Недоступно',
  unknown: 'Не проверено',
  active: 'Активна',
  not_set: 'Не задана',
  revoked: 'Отозвана',
};
