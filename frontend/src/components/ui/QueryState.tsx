import { PropsWithChildren, ReactNode, useEffect, useRef, useState } from 'react';
import type { UseQueryResult } from '@tanstack/react-query';

import { classifyApiError } from '../../api/errors';
import { Button } from './Button';
import { PageSkeleton } from './Skeleton';

/** After this long without a response we tell the user the server is slow. */
const SLOW_AFTER_MS = 6_000;

interface QueryStateProps<T> {
  query: Pick<UseQueryResult<T>, 'isPending' | 'isError' | 'error' | 'isFetching' | 'refetch'>;
  /** Custom skeleton; defaults to the generic PageSkeleton. */
  skeleton?: ReactNode;
  children: ReactNode;
}

/**
 * Wraps a React Query result and renders resilient states instead of a bare
 * "Загрузка...": skeleton on first load, a "server is slow" hint if it drags on,
 * and a friendly error card with a "Повторить" button on failure. It renders
 * `children` (the actual screen) only once data is available.
 */
export function QueryState<T>({ query, skeleton, children }: QueryStateProps<T>) {
  const slow = useSlowFlag(query.isPending || query.isFetching);

  if (query.isError) {
    return <ErrorState error={query.error} onRetry={() => void query.refetch()} />;
  }

  if (query.isPending) {
    return (
      <div className="space-y-3">
        {slow ? <SlowBanner /> : null}
        {skeleton ?? <PageSkeleton />}
      </div>
    );
  }

  return <>{children}</>;
}

/** Returns true once `active` has been true continuously for SLOW_AFTER_MS. */
export function useSlowFlag(active: boolean): boolean {
  const [slow, setSlow] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (active) {
      timer.current = setTimeout(() => setSlow(true), SLOW_AFTER_MS);
    } else {
      setSlow(false);
      if (timer.current) clearTimeout(timer.current);
    }
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [active]);

  return slow;
}

export function SlowBanner() {
  return (
    <div className="rounded-xl border border-amber-300/50 bg-amber-50 px-4 py-3 text-sm text-amber-800 dark:border-amber-400/20 dark:bg-amber-400/10 dark:text-amber-200">
      Сервер отвечает медленнее обычного. Пожалуйста, подождите…
    </div>
  );
}

interface ErrorStateProps {
  error: unknown;
  onRetry: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  const kind = classifyApiError(error);
  const message =
    kind === 'timeout'
      ? 'Превышено время ожидания ответа сервера.'
      : kind === 'network'
        ? 'Нет связи с сервером. Проверьте подключение (VPN) и попробуйте снова.'
        : kind === 'server'
          ? 'Сервер временно недоступен.'
          : 'Не удалось загрузить данные.';

  return (
    <div className="rounded-2xl border border-line bg-surface-raised p-6 text-center shadow-card">
      <p className="text-sm text-content-muted">{message}</p>
      <div className="mt-4 flex justify-center">
        <Button variant="secondary" onClick={onRetry}>
          Повторить
        </Button>
      </div>
    </div>
  );
}

/** Convenience wrapper for pages that just want children + default states. */
export function AsyncBoundary<T>({
  query,
  skeleton,
  children,
}: PropsWithChildren<QueryStateProps<T>>) {
  return (
    <QueryState query={query} skeleton={skeleton}>
      {children}
    </QueryState>
  );
}
