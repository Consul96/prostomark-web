import { PropsWithChildren } from 'react';

export function Table({ children }: PropsWithChildren) {
  return <div className="overflow-auto rounded-2xl bg-white shadow-card ring-1 ring-slate-100">{children}</div>;
}
