import { useQuery } from '@tanstack/react-query';

import { dashboardApi } from '../../api/dashboard';
import { Card } from '../../components/ui/Card';
import { Table } from '../../components/ui/Table';
import { formatDate } from '../../shared/format';
import { StatCard } from '../../widgets/StatCard';

export function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ['dashboard-summary'], queryFn: dashboardApi.summary });

  if (isLoading) {
    return <p>Загрузка...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard title="Товары" value={data?.products_count ?? 0} />
        <StatCard title="Документы" value={data?.documents_count ?? 0} />
        <StatCard title="Расчеты" value={data?.calculations_count ?? 0} />
        <StatCard title="Подписка" value={data?.subscription_status ?? 'n/a'} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="text-lg font-semibold">Аналитика</h3>
          <p className="mt-3 text-sm text-slate-600">Расчетов за 7 дней: {data?.analytics.calculations_last_7d ?? 0}</p>
          <div className="mt-3 space-y-1 text-sm text-slate-700">
            {Object.entries(data?.analytics.documents_by_status ?? {}).map(([status, count]) => (
              <p key={status}>
                {status}: {count}
              </p>
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold">Последние действия</h3>
          <div className="mt-3 space-y-2 text-sm text-slate-700">
            {data?.recent_actions?.map((log) => (
              <div key={log.id} className="rounded-xl bg-slate-50 p-3">
                <p className="font-medium">{log.action}</p>
                <p className="text-xs text-slate-500">{formatDate(log.created_at)}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Table>
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-4 py-3">Статус</th>
              <th className="px-4 py-3">Количество</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data?.analytics.documents_by_status ?? {}).map(([status, count]) => (
              <tr key={status} className="border-t border-slate-100">
                <td className="px-4 py-3">{status}</td>
                <td className="px-4 py-3">{count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Table>
    </div>
  );
}
