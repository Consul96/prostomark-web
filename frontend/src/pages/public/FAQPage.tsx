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
        <div key={item.q} className="rounded-2xl bg-surface-raised p-5 shadow-card ring-1 ring-line">
          <h2 className="font-semibold text-content">{item.q}</h2>
          <p className="mt-2 text-content-muted">{item.a}</p>
        </div>
      ))}
    </div>
  );
}
