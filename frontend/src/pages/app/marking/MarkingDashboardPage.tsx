import { useQuery } from '@tanstack/react-query';

import { markingApi } from '../../../api/marking';

const CARDS: Array<{ key: keyof NonNullable<ReturnType<typeof useDash>['data']>; label: string }> = [
  { key: 'active_applications', label: 'Активные заявки' },
  { key: 'cards_with_errors', label: 'Карточки с ошибками' },
  { key: 'gtin_pending_publication', label: 'GTIN ждут публикации' },
  { key: 'km_orders_processing', label: 'Заказы КМ в обработке' },
  { key: 'km_ready_to_receive', label: 'КМ готовы к получению' },
  { key: 'application_report_mismatches', label: 'Расхождения нанесения' },
  { key: 'circulation_pending_signature', label: 'Ввод — на подписании' },
  { key: 'circulation_rejected', label: 'Отклонённые документы' },
  { key: 'mchd_expiring', label: 'Истекающие МЧД' },
  { key: 'sign_agents_unavailable', label: 'Недоступные Sign Agent' },
];

function useDash() {
  return useQuery({ queryKey: ['marking', 'dashboard'], queryFn: markingApi.dashboard });
}

export function MarkingDashboardPage() {
  const { data, isLoading } = useDash();

  if (isLoading) return <p className="text-slate-500">Загрузка…</p>;
  if (!data) return <p className="text-slate-500">Нет данных</p>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        {CARDS.map((c) => (
          <div key={c.key} className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="text-3xl font-bold text-slate-900">{data[c.key] as number}</p>
            <p className="mt-1 text-xs text-slate-500">{c.label}</p>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h2 className="mb-3 font-heading text-lg font-semibold text-slate-900">Требуют внимания</h2>
        {data.attention.length === 0 ? (
          <p className="text-sm text-slate-500">Нет требующих внимания действий</p>
        ) : (
          <ul className="space-y-2">
            {data.attention.map((a, i) => (
              <li key={i} className="flex items-center justify-between rounded-lg bg-amber-50 px-3 py-2 text-sm">
                <span className="text-amber-900">{a.message}</span>
                <span className="rounded-full bg-amber-200 px-2 py-0.5 text-xs font-semibold text-amber-900">{a.count}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
