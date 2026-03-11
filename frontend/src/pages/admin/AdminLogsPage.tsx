import { useQuery } from '@tanstack/react-query';

import { adminApi } from '../../api/admin';
import { formatDate } from '../../shared/format';

export function AdminLogsPage() {
  const { data = [], isLoading } = useQuery({ queryKey: ['admin-logs'], queryFn: adminApi.logs });

  if (isLoading) {
    return <p>Загрузка...</p>;
  }

  return (
    <div className="overflow-auto rounded-2xl bg-white shadow-card ring-1 ring-slate-100">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-500">
          <tr>
            <th className="px-4 py-3">Action</th>
            <th className="px-4 py-3">Entity</th>
            <th className="px-4 py-3">User</th>
            <th className="px-4 py-3">Date</th>
          </tr>
        </thead>
        <tbody>
          {data.map((log) => (
            <tr key={log.id} className="border-t border-slate-100">
              <td className="px-4 py-3">{log.action}</td>
              <td className="px-4 py-3">{log.entity_type}</td>
              <td className="px-4 py-3">{log.user_id?.slice(0, 8) || '-'}</td>
              <td className="px-4 py-3">{formatDate(log.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
