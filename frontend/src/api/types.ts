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
