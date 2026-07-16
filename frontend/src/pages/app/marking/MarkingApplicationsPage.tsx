import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { PRODUCT_GROUPS, markingApi, type MarkingApplicationCreate } from '../../../api/marking';

const empty: MarkingApplicationCreate = { crpt_client_id: '', title: '', product_group: 'lp' };

export function MarkingApplicationsPage() {
  const qc = useQueryClient();
  const [form, setForm] = useState<MarkingApplicationCreate>(empty);
  const [open, setOpen] = useState(false);

  const { data: clients } = useQuery({ queryKey: ['marking', 'clients'], queryFn: markingApi.listClients });
  const { data: apps } = useQuery({ queryKey: ['marking', 'applications'], queryFn: markingApi.listApplications });

  const create = useMutation({
    mutationFn: () => markingApi.createApplication(form),
    onSuccess: () => {
      toast.success('Заявка создана');
      setForm(empty);
      setOpen(false);
      qc.invalidateQueries({ queryKey: ['marking', 'applications'] });
    },
    onError: () => toast.error('Не удалось создать заявку'),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-lg font-semibold text-slate-900">Заявки на маркировку</h2>
        <button onClick={() => setOpen(!open)} className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white">
          {open ? 'Отмена' : 'Новая заявка'}
        </button>
      </div>

      {open && (
        <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-5 md:grid-cols-2">
          <select className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            value={form.crpt_client_id} onChange={(e) => setForm({ ...form, crpt_client_id: e.target.value })}>
            <option value="">— Клиент —</option>
            {(clients ?? []).map((c) => <option key={c.id} value={c.id}>{c.name} ({c.inn})</option>)}
          </select>
          <select className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            value={form.product_group} onChange={(e) => setForm({ ...form, product_group: e.target.value })}>
            {PRODUCT_GROUPS.map((g) => <option key={g.code} value={g.code}>{g.title}</option>)}
          </select>
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2" placeholder="Название заявки"
            value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2" placeholder="Внешний номер заявки (опционально)"
            value={form.external_application_number ?? ''}
            onChange={(e) => setForm({ ...form, external_application_number: e.target.value })} />
          <button disabled={!form.crpt_client_id || !form.title || create.isPending}
            onClick={() => create.mutate()}
            className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 md:col-span-2">
            Создать заявку
          </button>
        </div>
      )}

      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Заявка</th>
              <th className="px-4 py-3">Товарная группа</th>
              <th className="px-4 py-3">Статус</th>
              <th className="px-4 py-3">Создана</th>
            </tr>
          </thead>
          <tbody>
            {(apps ?? []).map((a) => (
              <tr key={a.id} className="border-t border-slate-100">
                <td className="px-4 py-3 font-medium text-slate-900">{a.title}</td>
                <td className="px-4 py-3 text-slate-600">{a.product_group}</td>
                <td className="px-4 py-3 text-slate-600">{a.status}</td>
                <td className="px-4 py-3 text-slate-500">{new Date(a.created_at).toLocaleDateString('ru-RU')}</td>
              </tr>
            ))}
            {(apps ?? []).length === 0 && (
              <tr><td colSpan={4} className="px-4 py-6 text-center text-slate-500">Заявок пока нет</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
