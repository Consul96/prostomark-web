import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import { authApi } from '../api/auth';
import { useAuthStore } from '../store/authStore';

const navigation = [
  { to: '/app/dashboard', label: 'Dashboard' },
  { to: '/app/calculator', label: 'Калькулятор' },
  { to: '/app/products', label: 'Товары' },
  { to: '/app/documents', label: 'Документы' },
  { to: '/app/history', label: 'История' },
  { to: '/app/settings', label: 'Настройки' },
];

export function AppLayout() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const refreshToken = useAuthStore((state) => state.refreshToken);
  const clearSession = useAuthStore((state) => state.clearSession);

  const handleLogout = async () => {
    try {
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch {
      // noop
    } finally {
      clearSession();
      toast.success('Вы вышли из аккаунта');
      navigate('/login');
    }
  };

  return (
    <div className="grid min-h-screen grid-cols-1 bg-slate-50 lg:grid-cols-[260px_1fr]">
      <aside className="border-r border-slate-200 bg-white p-5">
        <div className="mb-8">
          <p className="font-heading text-2xl font-bold text-brand-700">ProstoMark</p>
          <p className="mt-1 text-xs text-slate-500">SaaS платформа маркировки</p>
        </div>
        <nav className="space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `block rounded-xl px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-brand-100 text-brand-800' : 'text-slate-600 hover:bg-slate-100'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex min-h-screen flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
          <div>
            <p className="text-sm text-slate-500">Пользователь</p>
            <p className="font-semibold text-slate-900">{user?.first_name} {user?.last_name}</p>
          </div>
          <button onClick={handleLogout} className="rounded-xl border border-slate-200 px-3 py-2 text-sm hover:bg-slate-50">
            Выйти
          </button>
        </header>

        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
