import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import {
  CONNECTION_STATUS_LABELS,
  PRODUCT_GROUPS,
  markingApi,
  type CrptClientCreate,
} from '../../../api/marking';

function StatusBadge({ value }: { value: string }) {
  const ok = value === 'ok' || value === 'active';
  const bad = value === 'expired' || value === 'unavailable' || value === 'cert_unavailable' || value === 'revoked';
  const cls = ok ? 'bg-emerald-100 text-emerald-800' : bad ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-600';
  return <span className={`rounded-full px-2 py-0.5 text-xs ${cls}`}>{CONNECTION_STATUS_LABELS[value] ?? value}</span>;
}

const empty: CrptClientCreate = { name: '', inn: '', environment: 'sandbox', product_groups: [] };

export function MarkingClientsPage() {
  const qc = useQueryClient();
  const [form, setForm] = useState<CrptClientCreate>(empty);
  const [open, setOpen] = useState(false);

  const { data: clients } = useQuery({ queryKey: ['marking', 'clients'], queryFn: markingApi.listClients });

  const create = useMutation({
    mutationFn: () => markingApi.createClient(form),
    onSuccess: () => {
      toast.success('Клиент создан');
      setForm(empty);
      setOpen(false);
      qc.invalidateQueries({ queryKey: ['marking', 'clients'] });
    },
    onError: () => toast.error('Не удалось создать клиента'),
  });

  const check = useMutation({
    mutationFn: (id: string) => markingApi.checkConnection(id),
    onSuccess: () => {
      toast.success('Проверка подключения выполнена');
      qc.invalidateQueries({ queryKey: ['marking', 'clients'] });
    },
  });

  const toggleGroup = (code: string) => {
    const set = new Set(form.product_groups ?? []);
    set.has(code) ? set.delete(code) : set.add(code);
    setForm({ ...form, product_groups: [...set] });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-lg font-semibold text-slate-900">Клиенты Честного знака</h2>
        <button onClick={() => setOpen(!open)} className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white">
          {open ? 'Отмена' : 'Новый клиент'}
        </button>
      </div>

      {open && (
        <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-5 md:grid-cols-2">
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Название"
            value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="ИНН"
            value={form.inn} onChange={(e) => setForm({ ...form, inn: e.target.value })} />
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="omsId"
            value={form.oms_id ?? ''} onChange={(e) => setForm({ ...form, oms_id: e.target.value })} />
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="omsConnection"
            value={form.oms_connection ?? ''} onChange={(e) => setForm({ ...form, oms_connection: e.target.value })} />
          <div className="md:col-span-2">
            <p className="mb-1 text-xs text-slate-500">Товарные группы</p>
            <div className="flex gap-2">
              {PRODUCT_GROUPS.map((g) => (
                <button key={g.code} type="button" onClick={() => toggleGroup(g.code)}
                  className={`rounded-lg border px-3 py-1.5 text-sm ${
                    form.product_groups?.includes(g.code) ? 'border-brand-500 bg-brand-50 text-brand-800' : 'border-slate-300 text-slate-600'
                  }`}>
                  {g.title}
                </button>
              ))}
            </div>
          </div>
          <button disabled={!form.name || !form.inn || create.isPending}
            onClick={() => create.mutate()}
            className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 md:col-span-2">
            Создать клиента
          </button>
        </div>
      )}

      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Клиент</th>
              <th className="px-4 py-3">ИНН</th>
              <th className="px-4 py-3">МЧД</th>
              <th className="px-4 py-3">True API</th>
              <th className="px-4 py-3">СУЗ</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {(clients ?? []).map((c) => (
              <tr key={c.id} className="border-t border-slate-100">
                <td className="px-4 py-3 font-medium text-slate-900">{c.name}</td>
                <td className="px-4 py-3 text-slate-600">{c.inn}</td>
                <td className="px-4 py-3"><StatusBadge value={c.mchd_status} /></td>
                <td className="px-4 py-3"><StatusBadge value={c.true_api_status} /></td>
                <td className="px-4 py-3"><StatusBadge value={c.suz_status} /></td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => check.mutate(c.id)} className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs hover:bg-slate-50">
                    Проверить
                  </button>
                </td>
              </tr>
            ))}
            {(clients ?? []).length === 0 && (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-500">Клиентов пока нет</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
