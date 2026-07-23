import { Monitor, Moon, Sun } from 'lucide-react';
import clsx from 'clsx';

import { useThemeStore, type ThemePreference } from '../../store/themeStore';

const options: Array<{ value: ThemePreference; label: string; icon: typeof Sun }> = [
  { value: 'light', label: 'Светлая тема', icon: Sun },
  { value: 'dark', label: 'Тёмная тема', icon: Moon },
  { value: 'system', label: 'Системная тема', icon: Monitor },
];

/**
 * Segmented light / dark / system theme switch.
 * Use `compact` in tight spaces (renders a single cycling button).
 */
export function ThemeToggle({ compact = false }: { compact?: boolean }) {
  const preference = useThemeStore((state) => state.preference);
  const setPreference = useThemeStore((state) => state.setPreference);
  const cycle = useThemeStore((state) => state.cycle);

  if (compact) {
    const active = options.find((option) => option.value === preference) ?? options[1];
    const Icon = active.icon;
    return (
      <button
        type="button"
        onClick={cycle}
        aria-label={`Тема: ${active.label}. Переключить`}
        title={active.label}
        className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-line text-content-muted transition hover:bg-surface-overlay hover:text-content"
      >
        <Icon className="h-4 w-4" />
      </button>
    );
  }

  return (
    <div
      role="radiogroup"
      aria-label="Тема оформления"
      className="inline-flex items-center gap-1 rounded-xl border border-line bg-surface-overlay p-1"
    >
      {options.map((option) => {
        const Icon = option.icon;
        const active = preference === option.value;
        return (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={option.label}
            title={option.label}
            onClick={() => setPreference(option.value)}
            className={clsx(
              'inline-flex h-8 w-8 items-center justify-center rounded-lg transition',
              active
                ? 'bg-surface-raised text-content shadow-sm'
                : 'text-content-subtle hover:text-content',
            )}
          >
            <Icon className="h-4 w-4" />
          </button>
        );
      })}
    </div>
  );
}
