import { apiClient } from './http';
import type { AuditLog, Company, CompanySubscription, User } from './types';

export interface AdminUserPayload {
  company_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'superadmin' | 'company_admin' | 'manager' | 'user';
  password: string;
  is_active: boolean;
  is_email_verified: boolean;
}

export const adminApi = {
  users: async () => {
    const { data } = await apiClient.get<User[]>('/admin/users');
    return data;
  },
  createUser: async (payload: AdminUserPayload) => {
    const { data } = await apiClient.post<User>('/admin/users', payload);
    return data;
  },
  companies: async () => {
    const { data } = await apiClient.get<Company[]>('/admin/companies');
    return data;
  },
  subscriptions: async () => {
    const { data } = await apiClient.get<CompanySubscription[]>('/admin/subscriptions');
    return data;
  },
  logs: async () => {
    const { data } = await apiClient.get<AuditLog[]>('/admin/logs');
    return data;
  },
};
