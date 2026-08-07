import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { markingApi } from '../../../api/marking';

export function MarkingSignAgentsPage() {
  const qc = useQueryClient();
  const [name, setName] = useState('');
  const [thumb, setThumb] = useState('');
  const [issuedKey, setIssuedKey] = useState<string | null>(null);

  const { data: agents } = useQuery({ queryKey: ['marking', 'agents'], queryFn: markingApi.listAgents });

  const create = useMutation({
    mutationFn: () => markingApi.createAgent({ name, certificate_thumbprint: thumb || undefined }),
    onSuccess: (agent) => {
      setIssuedKey(agent.api_key);
      setName('');
      setThumb('');
      qc.invalidateQueries({ queryKey: ['marking', 'agents'] });
      toast.success('Агент создан. Скопируйте API-ключ — он показывается один раз.');
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="font-heading text-lg font-semibold text-slate-900">Sign Agent (подпись через CryptoPro)</h2>

      {issuedKey && (
        <div className="rounded-2xl border border-emerald-300 bg-emerald-50 p-4 text-sm">
          <p className="font-medium text-emerald-900">API-ключ агента (показывается один раз):</p>
          <code className="mt-1 block break-all rounded bg-white p-2 font-mono text-xs">{issuedKey}</code>
        </div>
      )}

      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-5 md:grid-cols-3">
        <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Название агента"
          value={name} onChange={(e) => setName(e.target.value)} />
        <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Отпечаток сертификата (опц.)"
          value={thumb} onChange={(e) => setThumb(e.target.value)} />
        <button disabled={!name || create.isPending} onClick={() => create.mutate()}
          className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50">
          Создать агента
        </button>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Агент</th>
              <th className="px-4 py-3">Сертификат</th>
              <th className="px-4 py-3">Активен</th>
              <th className="px-4 py-3">Последний heartbeat</th>
            </tr>
          </thead>
          <tbody>
            {(agents ?? []).map((a) => (
              <tr key={a.id} className="border-t border-slate-100">
                <td className="px-4 py-3 font-medium text-slate-900">{a.name}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-500">{a.certificate_thumbprint ?? '—'}</td>
                <td className="px-4 py-3">{a.is_active ? 'Да' : 'Нет'}</td>
                <td className="px-4 py-3 text-slate-500">
                  {a.last_heartbeat_at ? new Date(a.last_heartbeat_at).toLocaleString('ru-RU') : '—'}
                </td>
              </tr>
            ))}
            {(agents ?? []).length === 0 && (
              <tr><td colSpan={4} className="px-4 py-6 text-center text-slate-500">Агентов пока нет</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
