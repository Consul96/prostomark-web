import type { AnalyticsBreakdownItem, AnalyticsTimeBucket } from '../../api/types';

function formatCompact(value: number) {
  return Intl.NumberFormat('ru-RU', { notation: 'compact', maximumFractionDigits: 1 }).format(value);
}

export function AnalyticsKpiGrid({
  items,
}: {
  items: Array<{ label: string; value: number | string | null; meta?: string | null; tone?: string; available?: boolean }>;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card ring-1 ring-white/60"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{item.label}</p>
          <p
            className={`mt-3 text-3xl font-semibold ${
              item.tone === 'danger'
                ? 'text-rose-600'
                : item.tone === 'success'
                  ? 'text-emerald-600'
                  : item.tone === 'brand'
                    ? 'text-brand-700'
                    : 'text-slate-950'
            }`}
          >
            {item.available === false ? 'N/A' : item.value ?? '0'}
          </p>
          <p className="mt-2 text-sm text-slate-500">{item.meta ?? ' '}</p>
        </div>
      ))}
    </div>
  );
}

export function LineChart({
  buckets,
  color = '#f97316',
}: {
  buckets: AnalyticsTimeBucket[];
  color?: string;
}) {
  const values = buckets.map((bucket) => bucket.total);
  const max = Math.max(...values, 1);
  const points = buckets
    .map((bucket, index) => {
      const x = buckets.length === 1 ? 0 : (index / Math.max(buckets.length - 1, 1)) * 100;
      const y = 100 - (bucket.total / max) * 100;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Events by day</p>
          <h3 className="mt-1 text-lg font-semibold text-slate-950">Динамика событий</h3>
        </div>
        <p className="text-sm text-slate-500">{formatCompact(values.reduce((sum, value) => sum + value, 0))}</p>
      </div>
      <div className="mt-5 rounded-2xl bg-slate-950/95 p-4">
        <svg viewBox="0 0 100 100" className="h-48 w-full overflow-visible">
          <defs>
            <linearGradient id="analyticsLineFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.32" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
          {[0, 25, 50, 75, 100].map((guide) => (
            <line key={guide} x1="0" y1={guide} x2="100" y2={guide} stroke="rgba(255,255,255,0.08)" strokeWidth="0.6" />
          ))}
          <polyline fill="none" stroke={color} strokeWidth="2.5" points={points} vectorEffect="non-scaling-stroke" />
          <polygon fill="url(#analyticsLineFill)" points={`0,100 ${points} 100,100`} />
        </svg>
        <div className="mt-3 grid grid-cols-3 gap-2 text-[11px] text-slate-300 md:grid-cols-6">
          {buckets.slice(-6).map((bucket) => (
            <div key={bucket.date} className="rounded-xl bg-white/5 px-2 py-1">
              <p>{bucket.date.slice(5)}</p>
              <p className="font-semibold text-white">{bucket.total}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function DonutChart({
  title,
  items,
}: {
  title: string;
  items: AnalyticsBreakdownItem[];
}) {
  const palette = ['#f97316', '#0f172a', '#1d4ed8', '#0f766e', '#ea580c', '#7c3aed'];
  const total = items.reduce((sum, item) => sum + item.value, 0);
  let offset = 0;

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{title}</p>
      <div className="mt-4 flex items-center gap-6">
        <div className="relative">
          <svg viewBox="0 0 120 120" className="h-36 w-36 -rotate-90">
            <circle cx="60" cy="60" r="42" fill="none" stroke="#e2e8f0" strokeWidth="16" />
            {items.map((item, index) => {
              const length = total === 0 ? 0 : (item.value / total) * 264;
              const segment = (
                <circle
                  key={item.key}
                  cx="60"
                  cy="60"
                  r="42"
                  fill="none"
                  stroke={palette[index % palette.length]}
                  strokeWidth="16"
                  strokeDasharray={`${length} 264`}
                  strokeDashoffset={-offset}
                  strokeLinecap="round"
                />
              );
              offset += length;
              return segment;
            })}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Total</p>
            <p className="text-2xl font-semibold text-slate-950">{total}</p>
          </div>
        </div>
        <div className="flex-1 space-y-3">
          {items.slice(0, 6).map((item, index) => (
            <div key={item.key} className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: palette[index % palette.length] }} />
                <p className="text-sm text-slate-700">{item.label}</p>
              </div>
              <p className="text-sm font-semibold text-slate-950">{item.value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function StackedBarChart({
  title,
  items,
}: {
  title: string;
  items: AnalyticsBreakdownItem[];
}) {
  const total = items.reduce((sum, item) => sum + item.value, 0);
  const palette = ['#f97316', '#0f172a', '#2563eb', '#0d9488', '#dc2626', '#7c3aed'];

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Breakdown</p>
          <h3 className="mt-1 text-lg font-semibold text-slate-950">{title}</h3>
        </div>
        <p className="text-sm text-slate-500">{total} total</p>
      </div>
      <div className="mt-5 flex h-4 overflow-hidden rounded-full bg-slate-100">
        {items.map((item, index) => (
          <div
            key={item.key}
            style={{ width: `${total === 0 ? 0 : (item.value / total) * 100}%`, backgroundColor: palette[index % palette.length] }}
          />
        ))}
      </div>
      <div className="mt-5 space-y-3">
        {items.slice(0, 6).map((item, index) => (
          <div key={item.key} className="flex items-center gap-4">
            <div className="flex min-w-0 flex-1 items-center gap-3">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: palette[index % palette.length] }} />
              <p className="truncate text-sm text-slate-700">{item.label}</p>
            </div>
            <p className="w-20 text-right text-sm font-semibold text-slate-950">{item.value}</p>
            <p className="w-16 text-right text-sm text-slate-500">
              {total === 0 ? '0%' : `${Math.round((item.value / total) * 100)}%`}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

