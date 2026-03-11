import { ButtonHTMLAttributes, PropsWithChildren } from 'react';
import clsx from 'clsx';

type ButtonVariant = 'primary' | 'secondary' | 'danger';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export function Button({ variant = 'primary', className, children, ...props }: PropsWithChildren<ButtonProps>) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50',
        variant === 'primary' && 'bg-brand-600 text-white hover:bg-brand-700',
        variant === 'secondary' && 'bg-white text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50',
        variant === 'danger' && 'bg-rose-600 text-white hover:bg-rose-700',
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
