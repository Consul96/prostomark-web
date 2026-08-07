import { PropsWithChildren, useMemo } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { useThemeEffect } from '../hooks/useTheme';
import { isRetriableError } from '../api/errors';

export function AppProviders({ children }: PropsWithChildren) {
  useThemeEffect();
  const client = useMemo(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Most screens (dashboard, reference lists, settings) don't need
            // second-by-second freshness. A 60s stale window avoids re-fetching
            // the same data every time the user tabs between screens, which is
            // the main source of redundant requests over a slow VPN.
            staleTime: 60_000,
            gcTime: 5 * 60_000,
            // Don't hammer the API when the user simply refocuses the window
            // (common on RDP). Do refetch after the network comes back.
            refetchOnWindowFocus: false,
            refetchOnReconnect: true,
            // Retry only transient failures (timeout / network / 5xx), once.
            // 4xx (incl. 401 handled by the axios refresh flow) never retries,
            // so a broken request can't turn into a long spinning wait.
            retry: (failureCount, error) => failureCount < 1 && isRetriableError(error),
            retryDelay: (attempt) => Math.min(1_000 * 2 ** attempt, 4_000),
          },
          mutations: {
            retry: 0,
          },
        },
      }),
    [],
  );

  return (
    <QueryClientProvider client={client}>
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgb(var(--surface-raised))',
            color: 'rgb(var(--content))',
            border: '1px solid rgb(var(--line))',
          },
        }}
      />
    </QueryClientProvider>
  );
}
