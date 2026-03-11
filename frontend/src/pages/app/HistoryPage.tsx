import { useQuery } from '@tanstack/react-query';

import { calculationsApi } from '../../api/calculations';
import { formatDate } from '../../shared/format';

export function HistoryPage() {
  const { data = [], isLoading } = useQuery({ queryKey: ['calculations'], queryFn: calculationsApi.list });

  if (isLoading) {
    return <p>Загрузка...</p>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">История расчетов</h1>
      <div className="overflow-auto rounded-2xl bg-white shadow-card ring-1 ring-slate-100">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Сумма</th>
              <th className="px-4 py-3">Валюта</th>
              <th className="px-4 py-3">Дата</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={item.id} className="border-t border-slate-100">
                <td className="px-4 py-3">{item.id.slice(0, 8)}</td>
                <td className="px-4 py-3">{item.total_amount}</td>
                <td className="px-4 py-3">{item.currency}</td>
                <td className="px-4 py-3">{formatDate(item.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
