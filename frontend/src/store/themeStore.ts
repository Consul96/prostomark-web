import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemePreference = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

interface ThemeState {
  /** User preference; `system` follows the OS setting. */
  preference: ThemePreference;
  setPreference: (preference: ThemePreference) => void;
  cycle: () => void;
}

/**
 * Persisted theme preference. Default is `dark` to match the
 * ProstoMark Analytics dark-theme concept, while still allowing the
 * user to switch to light or follow the system setting.
 */
export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      preference: 'dark',
      setPreference: (preference) => set({ preference }),
      cycle: () => {
        const order: ThemePreference[] = ['light', 'dark', 'system'];
        const next = order[(order.indexOf(get().preference) + 1) % order.length];
        set({ preference: next });
      },
    }),
    { name: 'prostomark-theme' },
  ),
);

export function resolveTheme(preference: ThemePreference): ResolvedTheme {
  if (preference === 'system') {
    if (typeof window === 'undefined') return 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return preference;
}
