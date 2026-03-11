import { apiClient } from './http';
import type { CompanySubscription, Plan } from './types';

interface CurrentPlanResponse {
  subscription: CompanySubscription | null;
  available_plans: Plan[];
}

export const billingApi = {
  currentPlan: async () => {
    const { data } = await apiClient.get<CurrentPlanResponse>('/billing/current-plan');
    return data;
  },
  checkout: async (planCode: string, billingCycle: 'month' | 'year') => {
    const { data } = await apiClient.post<{ checkout_url: string; session_id: string }>('/billing/checkout', {
      plan_code: planCode,
      billing_cycle: billingCycle,
    });
    return data;
  },
};
