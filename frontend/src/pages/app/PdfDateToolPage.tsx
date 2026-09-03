import { FormEvent, useState } from 'react';
import { CalendarRange, FileUp, WandSparkles } from 'lucide-react';
import toast from 'react-hot-toast';

import { pdfToolsApi } from '../../api/pdfTools';
import { Button } from '../../components/ui/Button';

function toDisplayDate(value: string): string {
  if (!value) return '';
  const [year, month, day] = value.split('-');
  return `${day}.${month}.${year}`;
}

export function PdfDateToolPage() {
  const [file, setFile] = useState<File | null>(null);
  const [manufactureDate, setManufactureDate] = useState('');
  const [currentExpiryDate, setCurrentExpiryDate] = useState('');
  const [newExpiryDate, setNewExpiryDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState<{ replacements: number; pagesChanged: number } | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) {
      toast.error('Выберите PDF-файл');
      return;
    }
    if (!manufactureDate || !currentExpiryDate || !newExpiryDate) {
      toast.error('Заполните все даты');
      return;
    }

    setLoading(true);
    setLastResult(null);
    try {
      const result = await pdfToolsApi.replaceExpiryDate({
        file,
        manufactureDate: toDisplayDate(manufactureDate),
        currentExpiryDate: toDisplayDate(currentExpiryDate),
        newExpiryDate: toDisplayDate(newExpiryDate),
      });

      const url = URL.createObjectURL(result.blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = result.filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);

      setLastResult({ replacements: result.replacements, pagesChanged: result.pagesChanged });
      toast.success(`Готово: заменено ${result.replacements} дат`);
    } catch (error) {
      toast.error('Не удалось обработать PDF. Проверьте введённые даты и сам файл.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-content">Замена даты в PDF</h1>
        <p className="mt-2 max-w-3xl text-sm text-content-muted">
          Модуль меняет дату окончания срока годности только на тех этикетках, где одновременно найдены указанная
          дата производства и текущая дата окончания срока годности. DataMatrix и штрихкоды не изменяются.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 rounded-2xl bg-surface-raised p-6 shadow-card ring-1 ring-line">
        <div>
          <label className="mb-2 block text-sm font-semibold text-content">PDF с этикетками</label>
          <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-dashed border-line bg-surface-overlay/40 p-4 transition hover:bg-surface-overlay">
            <FileUp className="h-5 w-5 text-content-muted" />
            <div className="min-w-0">
              <div className="truncate text-sm font-medium text-content">{file ? file.name : 'Выберите PDF-файл'}</div>
              <div className="text-xs text-content-subtle">До 500 МБ</div>
            </div>
            <input
              type="file"
              accept="application/pdf,.pdf"
              className="hidden"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <label className="space-y-2">
            <span className="flex items-center gap-2 text-sm font-semibold text-content">
              <CalendarRange className="h-4 w-4" /> Дата от
            </span>
            <input
              type="date"
              value={manufactureDate}
              onChange={(event) => setManufactureDate(event.target.value)}
              className="w-full rounded-xl border border-line bg-surface px-3 py-2.5 text-sm text-content outline-none focus:ring-2 focus:ring-brand-500/30"
            />
            <span className="block text-xs text-content-subtle">Manufacture date</span>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-semibold text-content">Текущая дата до</span>
            <input
              type="date"
              value={currentExpiryDate}
              onChange={(event) => setCurrentExpiryDate(event.target.value)}
              className="w-full rounded-xl border border-line bg-surface px-3 py-2.5 text-sm text-content outline-none focus:ring-2 focus:ring-brand-500/30"
            />
            <span className="block text-xs text-content-subtle">Какая дата сейчас стоит в PDF</span>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-semibold text-content">Заменить дату до на</span>
            <input
              type="date"
              value={newExpiryDate}
              onChange={(event) => setNewExpiryDate(event.target.value)}
              className="w-full rounded-xl border border-line bg-surface px-3 py-2.5 text-sm text-content outline-none focus:ring-2 focus:ring-brand-500/30"
            />
            <span className="block text-xs text-content-subtle">Новая Expiry date</span>
          </label>
        </div>

        <div className="rounded-xl bg-surface-overlay/60 p-4 text-sm text-content-muted">
          Например: <strong className="text-content">02.02.2026</strong> + текущая дата до{' '}
          <strong className="text-content">10.12.2028</strong> → заменить на{' '}
          <strong className="text-content">31.01.2029</strong>.
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={loading} className="gap-2">
            <WandSparkles className="h-4 w-4" />
            {loading ? 'Обрабатываем PDF…' : 'Заменить дату и скачать PDF'}
          </Button>
          {lastResult && (
            <span className="text-sm text-content-muted">
              Изменено этикеток: <strong className="text-content">{lastResult.replacements}</strong>, страниц:{' '}
              <strong className="text-content">{lastResult.pagesChanged}</strong>
            </span>
          )}
        </div>
      </form>

      <div className="rounded-2xl border border-line bg-surface-raised p-5 text-sm text-content-muted">
        Важно: обработка работает для PDF, где даты доступны как текст. Если PDF полностью состоит из изображений,
        модуль остановится и не будет менять файл вслепую.
      </div>
    </div>
  );
}
