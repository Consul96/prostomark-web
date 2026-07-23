import { PropsWithChildren } from 'react';

export function Table({ children }: PropsWithChildren) {
  return <div className="overflow-auto rounded-2xl bg-surface-raised shadow-card ring-1 ring-line">{children}</div>;
}
