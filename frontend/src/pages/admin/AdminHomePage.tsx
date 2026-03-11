import { useQuery } from '@tanstack/react-query';

import { adminApi } from '../../api/admin';
import { StatCard } from '../../widgets/StatCard';

export function AdminHomePage() {
  const { data: users = [] } = useQuery({ queryKey: ['admin-users'], queryFn: adminApi.users });
  const { data: companies = [] } = useQuery({ queryKey: ['admin-companies'], queryFn: adminApi.companies });
  const { data: subscriptions = [] } = useQuery({ queryKey: ['admin-subscriptions'], queryFn: adminApi.subscriptions });
  const { data: logs = [] } = useQuery({ queryKey: ['admin-logs'], queryFn: adminApi.logs });

  return (
    <div className="grid gap-4 md:grid-cols-4">
      <StatCard title="Пользователи" value={users.length} />
      <StatCard title="Компании" value={companies.length} />
      <StatCard title="Подписки" value={subscriptions.length} />
      <StatCard title="Логи" value={logs.length} />
    </div>
  );
}
