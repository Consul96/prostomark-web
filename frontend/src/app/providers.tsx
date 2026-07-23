import { PropsWithChildren, useMemo } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { useThemeEffect } from '../hooks/useTheme';

export function AppProviders({ children }: PropsWithChildren) {
  useThemeEffect();
  const client = useMemo(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 15_000,
            retry: 1,
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
