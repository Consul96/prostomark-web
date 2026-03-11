import { InputHTMLAttributes } from 'react';
import clsx from 'clsx';

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={clsx(
        'w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400',
        className,
      )}
      {...props}
    />
  );
}
