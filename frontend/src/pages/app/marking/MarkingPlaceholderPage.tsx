export function MarkingPlaceholderPage({ title, phase }: { title: string; phase: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
      <h2 className="font-heading text-lg font-semibold text-slate-900">{title}</h2>
      <p className="mt-2 text-sm text-slate-500">
        Раздел реализуется в {phase}. Модель данных, серверные эндпоинты и адаптеры интеграций
        зафиксированы; внешние вызовы подключаются после подтверждения схем документацией
        (см. docs/marking/crpt-api-mapping.md).
      </p>
    </div>
  );
}
