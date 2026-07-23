import { Card } from '../components/ui/Card';

interface StatCardProps {
  title: string;
  value: string | number;
  hint?: string;
}

export function StatCard({ title, value, hint }: StatCardProps) {
  return (
    <Card>
      <p className="text-xs uppercase tracking-wide text-content-subtle">{title}</p>
      <p className="mt-3 text-3xl font-bold text-content">{value}</p>
      {hint ? <p className="mt-2 text-sm text-content-muted">{hint}</p> : null}
    </Card>
  );
}
