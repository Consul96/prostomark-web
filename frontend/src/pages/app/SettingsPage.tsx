import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { billingApi } from '../../api/billing';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { QueryState } from '../../components/ui/QueryState';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAuthStore } from '../../store/authStore';

export function SettingsPage() {
  const user = useAuthStore((state) => state.user);
  const billingQuery = useQuery({ queryKey: ['billing-current-plan'], queryFn: billingApi.currentPlan });
  const data = billingQuery.data;

  const checkoutMutation = useMutation({
    mutationFn: ({ code, cycle }: { code: string; cycle: 'month' | 'year' }) => billingApi.checkout(code, cycle),
    onSuccess: (response) => {
      window.location.href = response.checkout_url;
    },
    onError: () => {
      toast.error('Не удалось создать платежную сессию');
    },
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Настройки</h1>

      <Card>
        <h2 className="text-lg font-semibold">Профиль</h2>
        <p className="mt-2 text-sm text-content-muted">{user?.first_name} {user?.last_name}</p>
        <p className="text-sm text-content-muted">{user?.email}</p>
        <p className="text-sm text-content-muted">Роль: {user?.role}</p>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold">Биллинг</h2>
        <QueryState
          query={billingQuery}
          skeleton={
            <div className="mt-2 space-y-3">
              <Skeleton className="h-5 w-64" />
              <div className="grid gap-3 md:grid-cols-3">
                <Skeleton className="h-24" />
                <Skeleton className="h-24" />
                <Skeleton className="h-24" />
              </div>
            </div>
          }
        >
          <>
            <p className="mt-2 text-sm text-content-muted">
              Текущая подписка: {data?.subscription?.plan?.name ?? 'Нет активного тарифа'} ({data?.subscription?.status ?? 'n/a'})
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {data?.available_plans.map((plan) => (
                <div key={plan.id} className="rounded-xl border border-line p-3">
                  <p className="font-semibold">{plan.name}</p>
                  <p className="text-sm text-content-subtle">{plan.price_month} ₽ / мес</p>
                  <div className="mt-3 flex gap-2">
                    <Button onClick={() => checkoutMutation.mutate({ code: plan.code, cycle: 'month' })}>
                      Оформить
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </>
        </QueryState>
      </Card>
    </div>
  );
}
