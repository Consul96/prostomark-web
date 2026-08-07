import { PageSkeleton } from './ui/Skeleton';

/**
 * Fallback shown while a lazily-loaded route chunk is downloading. On a slow
 * link the chunk fetch itself can take a moment, so we show a skeleton rather
 * than a blank screen or a bare "Загрузка...".
 */
export function RouteFallback() {
  return (
    <div className="p-6">
      <PageSkeleton />
    </div>
  );
}
