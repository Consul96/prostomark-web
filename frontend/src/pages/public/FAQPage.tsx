const faq = [
  {
    q: 'Поддерживается ли multi-tenant архитектура?',
    a: 'Да, все данные в личном кабинете изолированы по company_id.',
  },
  {
    q: 'Можно ли подключить Stripe для подписок?',
    a: 'Да, в платформе предусмотрены checkout и webhook-интеграции.',
  },
  {
    q: 'Как работает AI обработка документов?',
    a: 'После загрузки документа запускается фоновая задача, извлекается текст и формируется summary.',
  },
];

export function FAQPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">FAQ</h1>
      {faq.map((item) => (
        <div key={item.q} className="rounded-2xl bg-white p-5 shadow-card ring-1 ring-slate-100">
          <h2 className="font-semibold text-slate-900">{item.q}</h2>
          <p className="mt-2 text-slate-600">{item.a}</p>
        </div>
      ))}
    </div>
  );
}
