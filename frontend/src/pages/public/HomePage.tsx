import { Link } from 'react-router-dom';

export function HomePage() {
  return (
    <div className="space-y-8">
      <section className="rounded-3xl bg-gradient-to-br from-brand-700 to-brand-500 px-8 py-14 text-white shadow-card">
        <p className="mb-4 inline-flex rounded-full border border-white/30 px-3 py-1 text-xs">SaaS для маркировки и документов</p>
        <h1 className="max-w-3xl text-4xl font-bold leading-tight">ProstoMark: единая платформа для товаров, расчетов, документов и AI-аналитики</h1>
        <p className="mt-4 max-w-2xl text-white/90">
          Управляйте товарами, автоматизируйте обработку документов, контролируйте подписки и получайте оперативную аналитику в одном интерфейсе.
        </p>
        <div className="mt-8 flex gap-3">
          <Link to="/register" className="rounded-xl bg-white px-5 py-3 font-semibold text-brand-700">
            Начать бесплатно
          </Link>
          <Link to="/pricing" className="rounded-xl border border-white/40 px-5 py-3 font-semibold text-white">
            Посмотреть тарифы
          </Link>
        </div>
      </section>
    </div>
  );
}
