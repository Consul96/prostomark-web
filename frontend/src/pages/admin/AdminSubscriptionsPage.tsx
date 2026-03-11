import { useQuery } from '@tanstack/react-query';

import { adminApi } from '../../api/admin';
import { formatDate } from '../../shared/format';

export function AdminSubscriptionsPage() {
  const { data = [], isLoading } = useQuery({ queryKey: ['admin-subscriptions'], queryFn: adminApi.subscriptions });

  if (isLoading) {
    return <p>Загрузка...</p>;
  }

  return (
    <div className="overflow-auto rounded-2xl bg-white shadow-card ring-1 ring-slate-100">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-500">
          <tr>
            <th className="px-4 py-3">Компания</th>
            <th className="px-4 py-3">Тариф</th>
            <th className="px-4 py-3">Статус</th>
            <th className="px-4 py-3">Период до</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.id} className="border-t border-slate-100">
              <td className="px-4 py-3">{item.company_id.slice(0, 8)}</td>
              <td className="px-4 py-3">{item.plan?.name || '-'}</td>
              <td className="px-4 py-3">{item.status}</td>
              <td className="px-4 py-3">{formatDate(item.current_period_end)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
