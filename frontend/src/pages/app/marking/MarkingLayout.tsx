import { NavLink, Outlet } from 'react-router-dom';

const subnav = [
  { to: '/app/marking', label: 'Обзор', end: true },
  { to: '/app/marking/clients', label: 'Клиенты' },
  { to: '/app/marking/applications', label: 'Заявки' },
  { to: '/app/marking/products', label: 'Товары и GTIN' },
  { to: '/app/marking/km-orders', label: 'Заказы КМ' },
  { to: '/app/marking/application-reports', label: 'Нанесение' },
  { to: '/app/marking/circulation', label: 'Ввод в оборот' },
  { to: '/app/marking/sign-agents', label: 'Sign Agent' },
  { to: '/app/marking/history', label: 'История' },
];

export function MarkingLayout() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold text-slate-900">Честный знак</h1>
        <p className="text-sm text-slate-500">Полный процесс маркировки: НК, СУЗ и True API в едином контуре</p>
      </div>
      <nav className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
        {subnav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                isActive ? 'bg-brand-100 text-brand-800' : 'text-slate-600 hover:bg-slate-100'
              }`
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
