import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

import type { User } from '../api/types';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setSession: (accessToken: string, refreshToken: string, user: User) => void;
  setAccessToken: (accessToken: string) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setSession: (accessToken, refreshToken, user) => set({ accessToken, refreshToken, user }),
      setAccessToken: (accessToken) => set((state) => ({ ...state, accessToken })),
      clearSession: () => set({ accessToken: null, refreshToken: null, user: null }),
    }),
    {
      name: 'prostomark-auth',
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
