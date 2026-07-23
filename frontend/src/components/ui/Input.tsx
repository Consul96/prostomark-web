import { InputHTMLAttributes } from 'react';
import clsx from 'clsx';

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={clsx(
        'w-full rounded-xl border border-line bg-surface-raised px-3 py-2 text-sm text-content placeholder:text-content-subtle',
        className,
      )}
      {...props}
    />
  );
}
