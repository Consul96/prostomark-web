const plans = [
  { name: 'Trial', price: '0 ₽', description: 'Для теста платформы', features: ['3 пользователя', '20 AI документов'] },
  { name: 'Start', price: '1 990 ₽ / мес', description: 'Для небольших команд', features: ['10 пользователей', '200 AI документов'] },
  { name: 'Business', price: '5 990 ₽ / мес', description: 'Для масштабирования', features: ['50 пользователей', '2 000 AI документов'] },
];

export function PricingPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Тарифы</h1>
      <div className="grid gap-4 md:grid-cols-3">
        {plans.map((plan) => (
          <article key={plan.name} className="rounded-2xl bg-white p-5 shadow-card ring-1 ring-slate-100">
            <h2 className="text-xl font-bold">{plan.name}</h2>
            <p className="mt-2 text-2xl font-semibold text-brand-700">{plan.price}</p>
            <p className="mt-1 text-sm text-slate-500">{plan.description}</p>
            <ul className="mt-4 space-y-1 text-sm text-slate-700">
              {plan.features.map((feature) => (
                <li key={feature}>• {feature}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </div>
  );
}
