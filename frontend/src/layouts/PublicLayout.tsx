import { Link, Outlet } from 'react-router-dom';

export function PublicLayout() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200/70 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link to="/" className="font-heading text-xl font-bold text-brand-700">
            ProstoMark
          </Link>
          <nav className="flex items-center gap-4 text-sm font-medium text-slate-600">
            <Link to="/pricing" className="hover:text-brand-700">
              Тарифы
            </Link>
            <Link to="/faq" className="hover:text-brand-700">
              FAQ
            </Link>
            <Link to="/login" className="hover:text-brand-700">
              Вход
            </Link>
            <Link to="/register" className="rounded-xl bg-brand-600 px-4 py-2 text-white hover:bg-brand-700">
              Регистрация
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
