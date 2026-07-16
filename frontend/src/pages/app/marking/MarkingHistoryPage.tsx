import { useQuery } from '@tanstack/react-query';

import { markingApi } from '../../../api/marking';

export function MarkingHistoryPage() {
  const { data } = useQuery({ queryKey: ['marking', 'history'], queryFn: markingApi.history });

  return (
    <div className="space-y-4">
      <h2 className="font-heading text-lg font-semibold text-slate-900">История операций</h2>
      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Время</th>
              <th className="px-4 py-3">Операция</th>
              <th className="px-4 py-3">Объект</th>
              <th className="px-4 py-3">ИНН</th>
              <th className="px-4 py-3">Результат</th>
              <th className="px-4 py-3">Correlation ID</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((r) => (
              <tr key={r.id} className="border-t border-slate-100">
                <td className="px-4 py-3 text-slate-500">{new Date(r.created_at).toLocaleString('ru-RU')}</td>
                <td className="px-4 py-3 font-medium text-slate-900">{r.operation}</td>
                <td className="px-4 py-3 text-slate-600">{r.object_type ?? '—'}</td>
                <td className="px-4 py-3 text-slate-600">{r.client_inn ?? '—'}</td>
                <td className="px-4 py-3 text-slate-600">{r.result}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-400">{r.correlation_id ?? '—'}</td>
              </tr>
            ))}
            {(data ?? []).length === 0 && (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-500">Записей пока нет</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
