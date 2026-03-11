import { FormEvent, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { adminApi } from '../../api/admin';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

export function AdminUsersPage() {
  const queryClient = useQueryClient();
  const { data: users = [] } = useQuery({ queryKey: ['admin-users'], queryFn: adminApi.users });
  const { data: companies = [] } = useQuery({ queryKey: ['admin-companies'], queryFn: adminApi.companies });

  const [form, setForm] = useState({
    company_id: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'user' as 'superadmin' | 'company_admin' | 'manager' | 'user',
    password: '',
  });

  const mutation = useMutation({
    mutationFn: adminApi.createUser,
    onSuccess: () => {
      toast.success('Пользователь создан');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setForm({ company_id: '', email: '', first_name: '', last_name: '', role: 'user', password: '' });
    },
    onError: () => toast.error('Не удалось создать пользователя'),
  });

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    mutation.mutate({
      ...form,
      is_active: true,
      is_email_verified: true,
    });
  };

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="grid gap-3 rounded-2xl bg-white p-4 shadow-card ring-1 ring-slate-100 md:grid-cols-3">
        <select
          className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
          value={form.company_id}
          onChange={(e) => setForm((prev) => ({ ...prev, company_id: e.target.value }))}
          required
        >
          <option value="">Компания</option>
          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.name}
            </option>
          ))}
        </select>
        <Input placeholder="Email" value={form.email} onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))} required />
        <Input placeholder="Имя" value={form.first_name} onChange={(e) => setForm((prev) => ({ ...prev, first_name: e.target.value }))} required />
        <Input placeholder="Фамилия" value={form.last_name} onChange={(e) => setForm((prev) => ({ ...prev, last_name: e.target.value }))} required />
        <select
          className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
          value={form.role}
          onChange={(e) => setForm((prev) => ({ ...prev, role: e.target.value as typeof prev.role }))}
          required
        >
          <option value="user">user</option>
          <option value="manager">manager</option>
          <option value="company_admin">company_admin</option>
          <option value="superadmin">superadmin</option>
        </select>
        <Input
          placeholder="Временный пароль"
          type="password"
          value={form.password}
          onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
          required
        />
        <Button type="submit" disabled={mutation.isPending}>
          Создать
        </Button>
      </form>

      <div className="overflow-auto rounded-2xl bg-white shadow-card ring-1 ring-slate-100">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Имя</th>
              <th className="px-4 py-3">Роль</th>
              <th className="px-4 py-3">Компания</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-t border-slate-100">
                <td className="px-4 py-3">{user.email}</td>
                <td className="px-4 py-3">{user.first_name} {user.last_name}</td>
                <td className="px-4 py-3">{user.role}</td>
                <td className="px-4 py-3">{user.company_id.slice(0, 8)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
