import { PropsWithChildren } from 'react';
import clsx from 'clsx';

interface CardProps {
  className?: string;
}

export function Card({ className, children }: PropsWithChildren<CardProps>) {
  return <div className={clsx('rounded-2xl bg-white p-5 shadow-card ring-1 ring-slate-100', className)}>{children}</div>;
}
