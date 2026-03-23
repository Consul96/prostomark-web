export type Role = 'superadmin' | 'company_admin' | 'manager' | 'user';

export interface User {
  id: string;
  company_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
}

export interface AuthResponse {
  tokens: TokenPair;
  user: User;
}

export interface Product {
  id: string;
  company_id: string;
  name: string;
  brand: string | null;
  gtin: string | null;
  article: string | null;
  created_by: string;
  created_at: string;
}

export type DocumentStatus = 'uploaded' | 'processing' | 'processed' | 'failed';

export interface Document {
  id: string;
  company_id: string;
  product_id: string | null;
  document_type: string;
  number: string | null;
  document_date: string | null;
  file_path: string;
  original_filename: string;
  mime_type: string;
  status: DocumentStatus;
  extracted_text: string | null;
  ai_summary: string | null;
  created_by: string;
  created_at: string;
}

export interface Calculation {
  id: string;
  company_id: string;
  user_id: string;
  input_json: Record<string, unknown>;
  result_json: Record<string, unknown>;
  currency: string;
  total_amount: number;
  created_at: string;
}

export interface AuditLog {
  id: string;
  company_id: string | null;
  user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  meta_json: Record<string, unknown>;
  created_at: string;
}

export interface DashboardSummary {
  products_count: number;
  documents_count: number;
  calculations_count: number;
  subscription_status: string;
  recent_actions: AuditLog[];
  analytics: {
    documents_by_status: Record<string, number>;
    calculations_last_7d: number;
  };
}

export interface Plan {
  id: string;
  name: string;
  code: string;
  price_month: number;
  price_year: number;
  features_json: Record<string, unknown>;
  is_active: boolean;
}

export interface CompanySubscription {
  id: string;
  company_id: string;
  plan_id: string;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  status: string;
  current_period_start: string | null;
  current_period_end: string | null;
  created_at: string;
  plan: Plan;
}

export interface Company {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
}

export interface AnalyticsBreakdownItem {
  key: string;
  label: string;
  value: number;
}

export interface AnalyticsMetricCard {
  key: string;
  label: string;
  value: number | string | null;
  secondary: string | null;
  unit: string | null;
  tone: string;
  available: boolean;
}

export interface AnalyticsSourceStatus {
  key: string;
  label: string;
  path: string;
  available: boolean;
  records: number;
  updated_at: string | null;
  note: string | null;
}

export interface AnalyticsEventRecord {
  ts: number | null;
  dt: string | null;
  event: string;
  module: string;
  user_id: number | null;
  username: string | null;
  chat_id: number | null;
  thread_id: number | null;
  message_id: number | null;
  meta: Record<string, unknown>;
}

export interface AnalyticsTimeBucket {
  date: string;
  total: number;
  breakdown: Record<string, number>;
}

export interface AnalyticsSummary {
  period: string;
  range_start: string | null;
  range_end: string | null;
  cards: AnalyticsMetricCard[];
  event_breakdown: AnalyticsBreakdownItem[];
  module_breakdown: AnalyticsBreakdownItem[];
  source_status: AnalyticsSourceStatus[];
  highlights: string[];
}

export interface AnalyticsTimeseries {
  period: string;
  range_start: string | null;
  range_end: string | null;
  buckets: AnalyticsTimeBucket[];
  event_breakdown: AnalyticsBreakdownItem[];
  module_breakdown: AnalyticsBreakdownItem[];
  events: AnalyticsEventRecord[];
  total_events: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface AnalyticsUserStat {
  user_id: number | null;
  username: string;
  total_events: number;
  photos: number;
  commands: number;
  callbacks: number;
  errors: number;
  last_seen_at: string | null;
}

export interface AnalyticsThreadStat {
  thread_id: number;
  total_events: number;
  unique_users: number;
  last_seen_at: string | null;
}

export interface AnalyticsUsersTop {
  top_users: AnalyticsUserStat[];
  top_threads: AnalyticsThreadStat[];
}

export interface AnalyticsPhotoRecord {
  photo_id: string;
  timestamp: string | null;
  caption: string | null;
  status: string;
  reply_preview: string | null;
}

export interface AnalyticsPhotosSummary {
  total_photo_analyses: number;
  ok_feedback: number;
  mismatch_feedback: number;
  captionless_count: number;
  recent_cases: AnalyticsPhotoRecord[];
}

export interface AnalyticsPhotosHistory {
  items: AnalyticsPhotoRecord[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface AnalyticsNewsItem {
  news_id: string;
  title: string;
  source: string;
  category: string;
  link: string | null;
  published_at: string | null;
  cached_at: string | null;
  has_draft: boolean;
}

export interface AnalyticsNewsSummary {
  total_found: number;
  total_drafts: number;
  total_published: number;
  by_category: AnalyticsBreakdownItem[];
  by_source: AnalyticsBreakdownItem[];
  recent_items: AnalyticsNewsItem[];
  notes: string[];
}

export interface AnalyticsErrorRecord {
  scope: string;
  source: string;
  message: string;
  created_at: string | null;
  severity: string;
}

export interface AnalyticsAiUsageSummary {
  total_requests: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  total_cost_usd: number;
  last_request_at: string | null;
}

export interface AnalyticsSystemHealth {
  metrics: AnalyticsMetricCard[];
  recent_errors: AnalyticsErrorRecord[];
  anomalies: string[];
  ai_usage: AnalyticsAiUsageSummary;
  source_status: AnalyticsSourceStatus[];
}
