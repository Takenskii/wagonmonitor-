/** Auth context — wraps the app, exposes current user + login/logout/impersonate. */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

import { authApi } from '../api/auth';
import { adminApi } from '../api/admin';
import { authStorage, type AuthUser } from './storage';

interface AuthContextValue {
  user: AuthUser | null;
  originalUser: AuthUser | null;
  isImpersonating: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  impersonate: (userId: string) => Promise<void>;
  exitImpersonation: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => authStorage.getUser());
  const [originalUser, setOriginalUser] = useState<AuthUser | null>(() =>
    authStorage.getOriginalUser(),
  );

  useEffect(() => {
    const handler = () => {
      authStorage.clear();
      setUser(null);
      setOriginalUser(null);
    };
    window.addEventListener('auth:unauthorized', handler);
    return () => window.removeEventListener('auth:unauthorized', handler);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { token, ...identity } = await authApi.login(email, password);
    authStorage.set(token, identity);
    setUser(identity);
    setOriginalUser(null);
  }, []);

  const logout = useCallback(() => {
    authStorage.clear();
    setUser(null);
    setOriginalUser(null);
  }, []);

  const impersonate = useCallback(async (userId: string) => {
    const { token, ...identity } = await adminApi.impersonate(userId);
    authStorage.startImpersonation(token, identity);
    setOriginalUser(authStorage.getOriginalUser());
    setUser(identity);
  }, []);

  const exitImpersonation = useCallback(() => {
    authStorage.exitImpersonation();
    setUser(authStorage.getUser());
    setOriginalUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      originalUser,
      isImpersonating: originalUser !== null,
      login,
      logout,
      impersonate,
      exitImpersonation,
    }),
    [user, originalUser, login, logout, impersonate, exitImpersonation],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
