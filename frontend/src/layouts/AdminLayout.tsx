import { NavLink, Outlet } from 'react-router-dom';

const navigation = [
  { to: '/admin', label: 'Обзор' },
  { to: '/admin/users', label: 'Пользователи' },
  { to: '/admin/companies', label: 'Компании' },
  { to: '/admin/subscriptions', label: 'Подписки' },
  { to: '/admin/logs', label: 'Логи' },
];

export function AdminLayout() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Admin panel</h1>
      </header>
      <nav className="flex flex-wrap gap-2">
        {navigation.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/admin'}
            className={({ isActive }) =>
              `rounded-xl px-4 py-2 text-sm font-medium ${isActive ? 'bg-brand-600 text-white' : 'bg-white text-slate-600 ring-1 ring-slate-200'}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  );
}
