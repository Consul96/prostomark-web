import { useQuery } from '@tanstack/react-query';

import { adminApi } from '../../api/admin';
import { formatDate } from '../../shared/format';

export function AdminCompaniesPage() {
  const { data = [], isLoading } = useQuery({ queryKey: ['admin-companies'], queryFn: adminApi.companies });

  if (isLoading) {
    return <p>Загрузка...</p>;
  }

  return (
    <div className="overflow-auto rounded-2xl bg-white shadow-card ring-1 ring-slate-100">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-500">
          <tr>
            <th className="px-4 py-3">Название</th>
            <th className="px-4 py-3">Slug</th>
            <th className="px-4 py-3">Активна</th>
            <th className="px-4 py-3">Создана</th>
          </tr>
        </thead>
        <tbody>
          {data.map((company) => (
            <tr key={company.id} className="border-t border-slate-100">
              <td className="px-4 py-3">{company.name}</td>
              <td className="px-4 py-3">{company.slug}</td>
              <td className="px-4 py-3">{company.is_active ? 'Да' : 'Нет'}</td>
              <td className="px-4 py-3">{formatDate(company.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
