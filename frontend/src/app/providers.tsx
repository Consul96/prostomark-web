import { PropsWithChildren, useMemo } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

export function AppProviders({ children }: PropsWithChildren) {
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
      <Toaster position="top-right" />
    </QueryClientProvider>
  );
}
