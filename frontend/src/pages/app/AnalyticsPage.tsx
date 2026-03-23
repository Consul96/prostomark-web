import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, AlertTriangle, BarChart3, Camera, Download, Newspaper, RefreshCw, ServerCog, Users } from 'lucide-react';

import { analyticsApi } from '../../api/analytics';
import type { AnalyticsFilters } from '../../api/analytics';
import { getApiErrorMessage } from '../../api/errors';
import type {
  AnalyticsBreakdownItem,
  AnalyticsEventRecord,
  AnalyticsMetricCard,
  AnalyticsPhotoRecord,
} from '../../api/types';
import { Card } from '../../components/ui/Card';
import { Table } from '../../components/ui/Table';
import { useAuthStore } from '../../store/authStore';
import { formatDate } from '../../shared/format';
import { AnalyticsKpiGrid, DonutChart, LineChart, StackedBarChart } from '../../components/analytics/Charts';

type AnalyticsTab = 'summary' | 'usage' | 'photos' | 'news' | 'system' | 'ops';

const tabs: Array<{ key: AnalyticsTab; label: string; icon: typeof BarChart3 }> = [
  { key: 'summary', label: 'Summary', icon: BarChart3 },
  { key: 'usage', label: 'Usage', icon: Activity },
  { key: 'photos', label: 'Photos', icon: Camera },
  { key: 'news', label: 'News', icon: Newspaper },
  { key: 'system', label: 'System', icon: ServerCog },
  { key: 'ops', label: 'Ops', icon: Users },
];

function toneClass(tone: string) {
  if (tone === 'danger') return 'border-rose-200 bg-rose-50 text-rose-700';
  if (tone === 'success') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  if (tone === 'brand') return 'border-brand-200 bg-brand-50 text-brand-700';
  return 'border-slate-200 bg-slate-50 text-slate-700';
}

function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center">
      <p className="text-lg font-semibold text-slate-950">{title}</p>
      <p className="mt-2 text-sm text-slate-500">{description}</p>
    </div>
  );
}

function ErrorState({ error, retry }: { error: unknown; retry?: () => void }) {
  return (
    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-5 text-rose-800">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5" />
        <div>
          <p className="font-semibold">Не удалось загрузить данные аналитики</p>
          <p className="mt-1 text-sm">{getApiErrorMessage(error, 'Проверьте доступ к API analytics и конфигурацию путей к файлам.')}</p>
          {retry ? (
            <button
              type="button"
              onClick={retry}
              className="mt-3 inline-flex items-center gap-2 rounded-xl border border-rose-300 bg-white px-3 py-2 text-sm font-medium text-rose-700"
            >
              <RefreshCw className="h-4 w-4" />
              Повторить
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function FilterInput({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
      />
    </label>
  );
}

function SummaryHighlights({ items }: { items: string[] }) {
  return (
    <Card className="bg-slate-950 text-white ring-slate-900">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-300">Executive summary</p>
      <h2 className="mt-3 text-2xl font-semibold">Product analytics for Telegram Mini App</h2>
      <div className="mt-6 grid gap-3 md:grid-cols-3">
        {items.map((item) => (
          <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
            {item}
          </div>
        ))}
      </div>
    </Card>
  );
}

function EventsTable({ events }: { events: AnalyticsEventRecord[] }) {
  if (events.length === 0) {
    return <EmptyState title="Нет событий" description="Попробуйте расширить период или убрать часть фильтров." />;
  }

  return (
    <Table>
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-500">
          <tr>
            <th className="px-4 py-3">Время</th>
            <th className="px-4 py-3">Event</th>
            <th className="px-4 py-3">Module</th>
            <th className="px-4 py-3">User</th>
            <th className="px-4 py-3">Chat / Thread</th>
            <th className="px-4 py-3">Meta</th>
          </tr>
        </thead>
        <tbody>
          {events.map((item, index) => (
            <tr key={`${item.dt ?? 'event'}-${index}`} className="border-t border-slate-100 align-top">
              <td className="px-4 py-3 text-slate-600">{formatDate(item.dt)}</td>
              <td className="px-4 py-3 font-medium text-slate-950">{item.event}</td>
              <td className="px-4 py-3">
                <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${toneClass(item.module === 'photos' ? 'brand' : 'neutral')}`}>
                  {item.module}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-700">{item.username || item.user_id || 'Unknown'}</td>
              <td className="px-4 py-3 text-slate-600">
                {item.chat_id ?? '-'} / {item.thread_id ?? '-'}
              </td>
              <td className="px-4 py-3 text-xs text-slate-500">
                <pre className="max-w-[320px] whitespace-pre-wrap break-words font-mono">{JSON.stringify(item.meta, null, 2)}</pre>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Table>
  );
}

function PhotoTable({ items, title }: { items: AnalyticsPhotoRecord[]; title: string }) {
  return (
    <Card className="p-0">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-lg font-semibold text-slate-950">{title}</h3>
      </div>
      {items.length === 0 ? (
        <div className="p-5">
          <EmptyState title="Нет кейсов" description="В выбранном периоде нет подходящих фото-записей." />
        </div>
      ) : (
        <div className="divide-y divide-slate-100">
          {items.map((item) => (
            <div key={`${item.photo_id}-${item.timestamp ?? 'na'}`} className="px-5 py-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-slate-950">{item.caption || 'Без caption'}</p>
                  <p className="mt-1 text-xs text-slate-500">{formatDate(item.timestamp)} · {item.photo_id}</p>
                </div>
                <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${toneClass(item.status === 'ok' ? 'success' : 'danger')}`}>
                  {item.status}
                </span>
              </div>
              <p className="mt-3 text-sm text-slate-600">{item.reply_preview || 'Нет preview ответа'}</p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

function BreakdownTable({ title, items }: { title: string; items: AnalyticsBreakdownItem[] }) {
  return (
    <Card>
      <h3 className="text-lg font-semibold text-slate-950">{title}</h3>
      <div className="mt-4 space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-slate-500">Нет данных</p>
        ) : (
          items.map((item) => (
            <div key={item.key} className="flex items-center justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-sm text-slate-700">{item.label}</p>
              <p className="text-sm font-semibold text-slate-950">{item.value}</p>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}

export function AnalyticsPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('summary');
  const [period, setPeriod] = useState('30d');
  const [userId, setUserId] = useState('');
  const [chatId, setChatId] = useState('');
  const [threadId, setThreadId] = useState('');
  const [eventType, setEventType] = useState('');
  const [moduleName, setModuleName] = useState('');
  const [usageOffset, setUsageOffset] = useState(0);
  const [photosOffset, setPhotosOffset] = useState(0);
  const [mismatchOffset, setMismatchOffset] = useState(0);

  const baseFilters: AnalyticsFilters = {
    period,
    user_id: userId || undefined,
    chat_id: chatId || undefined,
    thread_id: threadId || undefined,
    event: eventType || undefined,
    module: moduleName || undefined,
  };

  const summaryQuery = useQuery({
    queryKey: ['analytics', 'summary', baseFilters],
    queryFn: () => analyticsApi.summary(baseFilters),
  });

  const usageQuery = useQuery({
    queryKey: ['analytics', 'usage', baseFilters, usageOffset],
    queryFn: () => analyticsApi.timeseries({ ...baseFilters, limit: 25, offset: usageOffset }),
    enabled: activeTab === 'summary' || activeTab === 'usage',
  });

  const usersQuery = useQuery({
    queryKey: ['analytics', 'users-top', baseFilters],
    queryFn: () => analyticsApi.usersTop(baseFilters),
    enabled: activeTab === 'summary' || activeTab === 'usage',
  });

  const photosSummaryQuery = useQuery({
    queryKey: ['analytics', 'photos-summary', baseFilters],
    queryFn: () => analyticsApi.photosSummary(baseFilters),
    enabled: activeTab === 'summary' || activeTab === 'photos',
  });

  const photosHistoryQuery = useQuery({
    queryKey: ['analytics', 'photos-history', baseFilters, photosOffset],
    queryFn: () => analyticsApi.photosHistory({ ...baseFilters, limit: 8, offset: photosOffset }),
    enabled: activeTab === 'photos',
  });

  const mismatchQuery = useQuery({
    queryKey: ['analytics', 'photos-mismatch', baseFilters, mismatchOffset],
    queryFn: () => analyticsApi.photosMismatch({ ...baseFilters, limit: 8, offset: mismatchOffset }),
    enabled: activeTab === 'photos',
  });

  const newsQuery = useQuery({
    queryKey: ['analytics', 'news', baseFilters],
    queryFn: () => analyticsApi.newsSummary(baseFilters),
    enabled: activeTab === 'summary' || activeTab === 'news',
  });

  const systemQuery = useQuery({
    queryKey: ['analytics', 'system', baseFilters],
    queryFn: () => analyticsApi.systemHealth(baseFilters),
    enabled: activeTab === 'summary' || activeTab === 'system',
  });

  if (user?.role !== 'superadmin' && user?.role !== 'manager') {
    return <EmptyState title="Раздел недоступен" description="Analytics доступен для manager и superadmin." />;
  }

  return (
    <div className="space-y-6">
      <div className="overflow-hidden rounded-[32px] bg-[radial-gradient(circle_at_top_left,_rgba(249,115,22,0.18),_transparent_34%),linear-gradient(135deg,#0f172a,#111827_55%,#1e293b)] p-6 text-white">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-300">Mini App analytics</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight">Unified analytics inside ProstoMark Mini App</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              Раздел собирает продуктовые события Telegram-бота, фото-историю, новости и системные сигналы в одном интерфейсе.
              Он остаётся безопасным даже при неполной конфигурации: отсутствующие источники показываются как empty state, а не ломают страницу.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <a
              href={analyticsApi.exportCsvUrl({ ...baseFilters, limit: 200 })}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/15 bg-white/10 px-4 py-3 text-sm font-medium text-white transition hover:bg-white/15"
            >
              <Download className="h-4 w-4" />
              Export CSV
            </a>
            <a
              href={analyticsApi.exportXlsxUrl({ ...baseFilters, limit: 200 })}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center justify-center gap-2 rounded-2xl bg-brand-500 px-4 py-3 text-sm font-medium text-white shadow-lg shadow-brand-500/25 transition hover:bg-brand-600"
            >
              <Download className="h-4 w-4" />
              Export XLSX
            </a>
          </div>
        </div>
      </div>

      <Card className="border border-slate-200 bg-white/95">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Filters</p>
            <h2 className="mt-2 text-xl font-semibold text-slate-950">Контекст анализа</h2>
            <p className="mt-2 text-sm text-slate-500">Фильтры применяются ко всем вкладкам. Для photo/news/system используются безопасные fallback-источники, если события недоступны.</p>
          </div>
          <button
            type="button"
            onClick={() => {
              summaryQuery.refetch();
              usageQuery.refetch();
              usersQuery.refetch();
              photosSummaryQuery.refetch();
              photosHistoryQuery.refetch();
              mismatchQuery.refetch();
              newsQuery.refetch();
              systemQuery.refetch();
            }}
            className="inline-flex items-center gap-2 self-start rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-6">
          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Период</span>
            <select
              value={period}
              onChange={(event) => {
                setPeriod(event.target.value);
                setUsageOffset(0);
                setPhotosOffset(0);
                setMismatchOffset(0);
              }}
              className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
            >
              <option value="7d">Последние 7 дней</option>
              <option value="30d">Последние 30 дней</option>
              <option value="90d">Последние 90 дней</option>
              <option value="today">Сегодня</option>
            </select>
          </label>
          <FilterInput label="user_id" value={userId} onChange={setUserId} placeholder="388740121" />
          <FilterInput label="chat_id" value={chatId} onChange={setChatId} placeholder="-100..." />
          <FilterInput label="thread_id" value={threadId} onChange={setThreadId} placeholder="12345" />
          <FilterInput label="event type" value={eventType} onChange={setEventType} placeholder="photo / cmd / callback" />
          <FilterInput label="module" value={moduleName} onChange={setModuleName} placeholder="photos / bot / core" />
        </div>
      </Card>

      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                active ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/25' : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {summaryQuery.isLoading ? <p className="text-sm text-slate-500">Загрузка summary...</p> : null}
      {summaryQuery.isError ? <ErrorState error={summaryQuery.error} retry={() => summaryQuery.refetch()} /> : null}

      {activeTab === 'summary' && summaryQuery.data ? (
        <div className="space-y-6">
          <SummaryHighlights items={summaryQuery.data.highlights} />
          <AnalyticsKpiGrid
            items={summaryQuery.data.cards.map((card: AnalyticsMetricCard) => ({
              label: card.label,
              value: card.value,
              meta: card.secondary,
              tone: card.tone,
              available: card.available,
            }))}
          />
          <div className="grid gap-6 xl:grid-cols-[1.6fr_1fr_1fr]">
            <LineChart buckets={usageQuery.data?.buckets ?? []} />
            <DonutChart title="Event type mix" items={summaryQuery.data.event_breakdown} />
            <StackedBarChart title="Module mix" items={summaryQuery.data.module_breakdown} />
          </div>
          <div className="grid gap-6 xl:grid-cols-2">
            <BreakdownTable title="Источники данных" items={summaryQuery.data.source_status.map((item) => ({ key: item.key, label: `${item.label}${item.available ? '' : ' · unavailable'}`, value: item.records }))} />
            <BreakdownTable title="Top event types" items={summaryQuery.data.event_breakdown} />
          </div>
          <div className="grid gap-6 xl:grid-cols-2">
            <Card>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-950">Top users</h3>
                <span className="text-sm text-slate-500">Usage tab</span>
              </div>
              <div className="mt-4 space-y-3">
                {usersQuery.data?.top_users?.slice(0, 5).map((item) => (
                  <div key={`${item.user_id ?? 'unknown'}-${item.username}`} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                    <div>
                      <p className="font-medium text-slate-950">{item.username}</p>
                      <p className="text-xs text-slate-500">photos {item.photos} · callbacks {item.callbacks}</p>
                    </div>
                    <p className="text-sm font-semibold text-slate-950">{item.total_events}</p>
                  </div>
                )) ?? <p className="text-sm text-slate-500">Нет данных</p>}
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-950">System watch</h3>
                <span className="text-sm text-slate-500">Health tab</span>
              </div>
              <div className="mt-4 space-y-3">
                {systemQuery.data?.anomalies?.slice(0, 5).map((item) => (
                  <div key={item} className="rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700">
                    {item}
                  </div>
                )) ?? <p className="text-sm text-slate-500">Нет аномалий</p>}
              </div>
            </Card>
          </div>
        </div>
      ) : null}

      {activeTab === 'usage' ? (
        usageQuery.isError ? (
          <ErrorState error={usageQuery.error} retry={() => usageQuery.refetch()} />
        ) : usageQuery.data ? (
          <div className="space-y-6">
            <div className="grid gap-6 xl:grid-cols-[1.6fr_1fr_1fr]">
              <LineChart buckets={usageQuery.data.buckets} />
              <DonutChart title="Event types" items={usageQuery.data.event_breakdown} />
              <StackedBarChart title="Modules" items={usageQuery.data.module_breakdown} />
            </div>
            <div className="grid gap-6 xl:grid-cols-2">
              <Card>
                <h3 className="text-lg font-semibold text-slate-950">Top users</h3>
                <div className="mt-4 space-y-3">
                  {usersQuery.data?.top_users.map((item) => (
                    <div key={`${item.user_id ?? 'unknown'}-${item.username}`} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                      <div>
                        <p className="font-medium text-slate-950">{item.username}</p>
                        <p className="text-xs text-slate-500">cmd {item.commands} · photo {item.photos} · errors {item.errors}</p>
                      </div>
                      <p className="text-sm font-semibold text-slate-950">{item.total_events}</p>
                    </div>
                  )) ?? <p className="text-sm text-slate-500">Нет данных</p>}
                </div>
              </Card>
              <Card>
                <h3 className="text-lg font-semibold text-slate-950">Top threads</h3>
                <div className="mt-4 space-y-3">
                  {usersQuery.data?.top_threads.map((item) => (
                    <div key={item.thread_id} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                      <div>
                        <p className="font-medium text-slate-950">Thread {item.thread_id}</p>
                        <p className="text-xs text-slate-500">users {item.unique_users}</p>
                      </div>
                      <p className="text-sm font-semibold text-slate-950">{item.total_events}</p>
                    </div>
                  )) ?? <p className="text-sm text-slate-500">Нет данных</p>}
                </div>
              </Card>
            </div>
            <EventsTable events={usageQuery.data.events} />
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-500">
                Показано {usageQuery.data.events.length} из {usageQuery.data.total_events}
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setUsageOffset((current) => Math.max(0, current - 25))}
                  disabled={usageOffset === 0}
                  className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
                >
                  Назад
                </button>
                <button
                  type="button"
                  onClick={() => setUsageOffset((current) => current + 25)}
                  disabled={!usageQuery.data.has_more}
                  className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
                >
                  Дальше
                </button>
              </div>
            </div>
          </div>
        ) : null
      ) : null}

      {activeTab === 'photos' ? (
        photosSummaryQuery.isError ? (
          <ErrorState error={photosSummaryQuery.error} retry={() => photosSummaryQuery.refetch()} />
        ) : (
          <div className="space-y-6">
            <AnalyticsKpiGrid
              items={[
                { label: 'Total photo analyses', value: photosSummaryQuery.data?.total_photo_analyses ?? 0, meta: 'История photo_history.json', tone: 'brand' },
                { label: 'OK feedback', value: photosSummaryQuery.data?.ok_feedback ?? 0, meta: 'Статус ok в mismatch log', tone: 'success' },
                { label: 'Mismatch feedback', value: photosSummaryQuery.data?.mismatch_feedback ?? 0, meta: 'Не-ok статусы', tone: 'danger' },
                { label: 'Captionless cases', value: photosSummaryQuery.data?.captionless_count ?? 0, meta: 'Запросы без caption' },
              ]}
            />
            <div className="grid gap-6 xl:grid-cols-2">
              <PhotoTable items={photosSummaryQuery.data?.recent_cases ?? []} title="Последние кейсы" />
              <Card>
                <h3 className="text-lg font-semibold text-slate-950">Signals</h3>
                <div className="mt-4 space-y-3">
                  <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">Photos tab собирает историю анализа и обратную связь mismatch/ok без отдельной БД, напрямую из существующих JSON-файлов.</div>
                  <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">Для роста объёма данных следующий шаг: вынести photo history и feedback в persistent storage и добавить полнотекстовый поиск по caption.</div>
                </div>
              </Card>
            </div>
            <div className="grid gap-6 xl:grid-cols-2">
              {photosHistoryQuery.data ? <PhotoTable items={photosHistoryQuery.data.items} title="История фото" /> : null}
              {mismatchQuery.data ? <PhotoTable items={mismatchQuery.data.items} title="Mismatch cases" /> : null}
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <p className="text-sm text-slate-500">История фото: {photosHistoryQuery.data?.total ?? 0}</p>
                <div className="flex gap-2">
                  <button type="button" onClick={() => setPhotosOffset((current) => Math.max(0, current - 8))} disabled={photosOffset === 0} className="rounded-xl border border-slate-200 px-3 py-2 text-sm disabled:opacity-50">Назад</button>
                  <button type="button" onClick={() => setPhotosOffset((current) => current + 8)} disabled={!photosHistoryQuery.data?.has_more} className="rounded-xl border border-slate-200 px-3 py-2 text-sm disabled:opacity-50">Дальше</button>
                </div>
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <p className="text-sm text-slate-500">Mismatch cases: {mismatchQuery.data?.total ?? 0}</p>
                <div className="flex gap-2">
                  <button type="button" onClick={() => setMismatchOffset((current) => Math.max(0, current - 8))} disabled={mismatchOffset === 0} className="rounded-xl border border-slate-200 px-3 py-2 text-sm disabled:opacity-50">Назад</button>
                  <button type="button" onClick={() => setMismatchOffset((current) => current + 8)} disabled={!mismatchQuery.data?.has_more} className="rounded-xl border border-slate-200 px-3 py-2 text-sm disabled:opacity-50">Дальше</button>
                </div>
              </div>
            </div>
          </div>
        )
      ) : null}

      {activeTab === 'news' ? (
        newsQuery.isError ? (
          <ErrorState error={newsQuery.error} retry={() => newsQuery.refetch()} />
        ) : newsQuery.data ? (
          <div className="space-y-6">
            <AnalyticsKpiGrid
              items={[
                { label: 'Total news found', value: newsQuery.data.total_found, meta: 'Из news_cache.json', tone: 'brand' },
                { label: 'Draft stats', value: newsQuery.data.total_drafts, meta: 'Черновики в news_drafts.json' },
                { label: 'Published stats', value: newsQuery.data.total_published, meta: 'Требует отдельного persistent флага' },
                { label: 'Sources', value: newsQuery.data.by_source.length, meta: 'Активные домены источников' },
              ]}
            />
            <div className="grid gap-6 xl:grid-cols-2">
              <DonutChart title="By category" items={newsQuery.data.by_category} />
              <StackedBarChart title="By source" items={newsQuery.data.by_source} />
            </div>
            <Card>
              <h3 className="text-lg font-semibold text-slate-950">Recent news</h3>
              <div className="mt-4 space-y-3">
                {newsQuery.data.recent_items.map((item) => (
                  <div key={item.news_id} className="rounded-2xl border border-slate-200 p-4">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="font-medium text-slate-950">{item.title}</p>
                        <p className="mt-1 text-xs text-slate-500">
                          {item.source} · {item.category} · {formatDate(item.cached_at)}
                        </p>
                      </div>
                      <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${toneClass(item.has_draft ? 'brand' : 'neutral')}`}>
                        {item.has_draft ? 'draft ready' : 'cache only'}
                      </span>
                    </div>
                    {item.link ? (
                      <a href={item.link} target="_blank" rel="noreferrer" className="mt-3 inline-block text-sm font-medium text-brand-700 hover:text-brand-800">
                        Открыть источник
                      </a>
                    ) : null}
                  </div>
                ))}
              </div>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold text-slate-950">Notes</h3>
              <div className="mt-4 space-y-3">
                {newsQuery.data.notes.map((item) => (
                  <div key={item} className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">{item}</div>
                ))}
              </div>
            </Card>
          </div>
        ) : null
      ) : null}

      {activeTab === 'system' ? (
        systemQuery.isError ? (
          <ErrorState error={systemQuery.error} retry={() => systemQuery.refetch()} />
        ) : systemQuery.data ? (
          <div className="space-y-6">
            <AnalyticsKpiGrid
              items={systemQuery.data.metrics.map((metric) => ({
                label: metric.label,
                value: metric.value,
                meta: metric.secondary,
                available: metric.available,
              }))}
            />
            <div className="grid gap-6 xl:grid-cols-2">
              <Card>
                <h3 className="text-lg font-semibold text-slate-950">Recent errors & anomalies</h3>
                <div className="mt-4 space-y-3">
                  {systemQuery.data.recent_errors.length === 0 ? (
                    <p className="text-sm text-slate-500">Нет явных ошибок за период.</p>
                  ) : (
                    systemQuery.data.recent_errors.map((item) => (
                      <div key={`${item.source}-${item.created_at ?? 'na'}-${item.message}`} className={`rounded-2xl border p-4 ${item.severity === 'critical' ? 'border-rose-200 bg-rose-50' : 'border-amber-200 bg-amber-50'}`}>
                        <p className="font-medium text-slate-950">{item.message}</p>
                        <p className="mt-1 text-xs text-slate-500">{item.scope} · {item.source} · {formatDate(item.created_at)}</p>
                      </div>
                    ))
                  )}
                </div>
              </Card>
              <Card>
                <h3 className="text-lg font-semibold text-slate-950">AI usage</h3>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Requests</p>
                    <p className="mt-2 text-2xl font-semibold text-slate-950">{systemQuery.data.ai_usage.total_requests}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Total tokens</p>
                    <p className="mt-2 text-2xl font-semibold text-slate-950">{systemQuery.data.ai_usage.total_tokens}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Prompt / completion</p>
                    <p className="mt-2 text-2xl font-semibold text-slate-950">
                      {systemQuery.data.ai_usage.total_prompt_tokens} / {systemQuery.data.ai_usage.total_completion_tokens}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Cost USD</p>
                    <p className="mt-2 text-2xl font-semibold text-slate-950">${systemQuery.data.ai_usage.total_cost_usd.toFixed(4)}</p>
                  </div>
                </div>
              </Card>
            </div>
            <BreakdownTable title="Source health" items={systemQuery.data.source_status.map((item) => ({ key: item.key, label: `${item.label}${item.note ? ` · ${item.note}` : ''}`, value: item.records }))} />
          </div>
        ) : null
      ) : null}

      {activeTab === 'ops' ? (
        <div className="space-y-6">
          <Card className="bg-slate-950 text-white ring-slate-900">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-300">Ops</p>
            <h2 className="mt-3 text-2xl font-semibold">Operational layer prepared for the next API iteration</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
              В текущем проекте нет устойчивого persistent-источника по задачам, SLA и эффективности сотрудников, поэтому вкладка пока выступает как каркас.
              Интерфейс уже готов к подключению будущего API без ломки Mini App.
            </p>
          </Card>
          <div className="grid gap-6 lg:grid-cols-3">
            <Card>
              <h3 className="text-lg font-semibold text-slate-950">Overview</h3>
              <p className="mt-3 text-sm text-slate-500">Подключить overview по задачам, входящим потокам и загрузке команд.</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold text-slate-950">Statuses & SLA</h3>
              <p className="mt-3 text-sm text-slate-500">Добавить статусы, lead time, first-response и SLA breach counters.</p>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold text-slate-950">Employee summary</h3>
              <p className="mt-3 text-sm text-slate-500">Подготовлено место для перформанса сотрудников и менеджеров после появления источника данных.</p>
            </Card>
          </div>
          <EmptyState title="Ops API пока не подключён" description="Следующий шаг: описать persistent storage и endpoint contracts для operational tracker." />
        </div>
      ) : null}
    </div>
  );
}
