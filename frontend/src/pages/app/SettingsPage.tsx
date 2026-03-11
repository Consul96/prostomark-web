import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { billingApi } from '../../api/billing';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { useAuthStore } from '../../store/authStore';

export function SettingsPage() {
  const user = useAuthStore((state) => state.user);
  const { data, isLoading } = useQuery({ queryKey: ['billing-current-plan'], queryFn: billingApi.currentPlan });

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
        <p className="mt-2 text-sm text-slate-600">{user?.first_name} {user?.last_name}</p>
        <p className="text-sm text-slate-600">{user?.email}</p>
        <p className="text-sm text-slate-600">Роль: {user?.role}</p>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold">Биллинг</h2>
        {isLoading ? (
          <p className="mt-2 text-sm text-slate-500">Загрузка...</p>
        ) : (
          <>
            <p className="mt-2 text-sm text-slate-600">
              Текущая подписка: {data?.subscription?.plan?.name ?? 'Нет активного тарифа'} ({data?.subscription?.status ?? 'n/a'})
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {data?.available_plans.map((plan) => (
                <div key={plan.id} className="rounded-xl border border-slate-200 p-3">
                  <p className="font-semibold">{plan.name}</p>
                  <p className="text-sm text-slate-500">{plan.price_month} ₽ / мес</p>
                  <div className="mt-3 flex gap-2">
                    <Button onClick={() => checkoutMutation.mutate({ code: plan.code, cycle: 'month' })}>
                      Оформить
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
