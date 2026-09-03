import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  BarChart3,
  Calculator,
  CalendarRange,
  FileText,
  History,
  LayoutDashboard,
  LogOut,
  Package,
  ScanLine,
  Settings,
  type LucideIcon,
} from 'lucide-react';

import { authApi } from '../api/auth';
import type { Role } from '../api/types';
import { useAuthStore } from '../store/authStore';
import { ThemeToggle } from '../components/ui/ThemeToggle';

interface NavigationItem {
  to: string;
  label: string;
  icon: LucideIcon;
  roles?: Role[];
}

const navigation: NavigationItem[] = [
  { to: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/analytics', label: 'Аналитика', icon: BarChart3, roles: ['superadmin', 'manager'] },
  { to: '/app/calculator', label: 'Калькулятор', icon: Calculator },
  { to: '/app/products', label: 'Товары', icon: Package },
  { to: '/app/marking', label: 'Честный знак', icon: ScanLine },
  { to: '/app/documents', label: 'Документы', icon: FileText },
  { to: '/app/pdf-date-tool', label: 'Даты PDF', icon: CalendarRange },
  { to: '/app/history', label: 'История', icon: History },
  { to: '/app/settings', label: 'Настройки', icon: Settings },
];

export function AppLayout() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const refreshToken = useAuthStore((state) => state.refreshToken);
  const clearSession = useAuthStore((state) => state.clearSession);
  const navigationItems = navigation.filter(
    (item) => !item.roles || (user ? item.roles.includes(user.role) : false),
  );

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

  const initials = `${user?.first_name?.[0] ?? ''}${user?.last_name?.[0] ?? ''}`.toUpperCase() || 'PM';

  return (
    <div className="grid min-h-screen grid-cols-1 bg-surface text-content lg:grid-cols-[264px_1fr]">
      <aside className="hidden flex-col border-r border-line bg-surface-raised/70 p-5 backdrop-blur lg:flex">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600 font-heading text-lg font-bold text-white">
            P
          </div>
          <div>
            <p className="font-heading text-lg font-bold text-content">ProstoMark</p>
            <p className="text-xs text-content-subtle">Платформа маркировки</p>
          </div>
        </div>
        <nav className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                    isActive
                      ? 'bg-accent-soft text-accent ring-1 ring-accent/20'
                      : 'text-content-muted hover:bg-surface-overlay hover:text-content'
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
        <div className="mt-auto pt-6">
          <div className="flex items-center justify-between rounded-xl border border-line bg-surface-overlay/60 px-3 py-2">
            <span className="text-xs text-content-subtle">Тема</span>
            <ThemeToggle />
          </div>
        </div>
      </aside>

      <div className="flex min-h-screen flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-line bg-surface-raised/80 px-6 py-4 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 font-heading text-sm font-bold text-white lg:hidden">
              P
            </div>
            <div>
              <p className="text-xs text-content-subtle">Пользователь</p>
              <p className="font-semibold text-content">
                {user?.first_name} {user?.last_name}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="lg:hidden">
              <ThemeToggle compact />
            </span>
            <div className="hidden h-9 w-9 items-center justify-center rounded-full bg-surface-overlay text-sm font-semibold text-content-muted sm:flex">
              {initials}
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-2 rounded-xl border border-line px-3 py-2 text-sm font-medium text-content-muted transition hover:bg-surface-overlay hover:text-content"
            >
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">Выйти</span>
            </button>
          </div>
        </header>

        {/* Mobile nav */}
        <nav className="flex gap-1 overflow-x-auto border-b border-line bg-surface-raised/60 px-4 py-2 lg:hidden">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `inline-flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
                    isActive ? 'bg-accent-soft text-accent' : 'text-content-muted hover:bg-surface-overlay'
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
