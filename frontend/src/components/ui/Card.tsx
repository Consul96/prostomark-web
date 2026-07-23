import { PropsWithChildren } from 'react';
import clsx from 'clsx';

interface CardProps {
  className?: string;
}

export function Card({ className, children }: PropsWithChildren<CardProps>) {
  return (
    <div className={clsx('rounded-2xl bg-surface-raised p-5 shadow-card ring-1 ring-line', className)}>{children}</div>
  );
}
