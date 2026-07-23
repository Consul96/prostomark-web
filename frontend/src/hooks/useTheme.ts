import { useEffect } from 'react';

import { resolveTheme, useThemeStore, type ResolvedTheme } from '../store/themeStore';

/**
 * Applies the resolved theme to <html> by toggling the `dark` class and
 * keeps it in sync with the OS setting when the preference is `system`.
 * Mount once near the app root.
 */
export function useThemeEffect(): ResolvedTheme {
  const preference = useThemeStore((state) => state.preference);
  const resolved = resolveTheme(preference);

  useEffect(() => {
    const root = document.documentElement;
    const apply = () => {
      const next = resolveTheme(preference);
      root.classList.toggle('dark', next === 'dark');
    };
    apply();

    if (preference !== 'system') return;
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    media.addEventListener('change', apply);
    return () => media.removeEventListener('change', apply);
  }, [preference]);

  return resolved;
}
