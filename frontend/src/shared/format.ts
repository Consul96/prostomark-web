export function formatDate(value: string | null | undefined): string {
  if (!value) return '-';
  const date = new Date(value);
  return Intl.DateTimeFormat('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}
