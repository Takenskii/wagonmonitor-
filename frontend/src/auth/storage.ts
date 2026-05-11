/**
 * JWT + identity cache in localStorage + masquerade (impersonation) state.
 *
 * Single point of mutation — every read/write of auth state goes through here.
 */
const TOKEN_KEY = 'wm_token';
const USER_KEY = 'wm_user';
const ORIGINAL_TOKEN_KEY = 'wm_original_token';
const ORIGINAL_USER_KEY = 'wm_original_user';

export interface AuthUser {
  user_id: string;
  email: string;
  full_name: string | null;
  role: 'superadmin' | 'admin' | 'user';
  company_id: string;
  company_name: string;
}

const readJson = <T>(key: string): T | null => {
  const raw = localStorage.getItem(key);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
};

export const authStorage = {
  getToken: (): string | null => localStorage.getItem(TOKEN_KEY),
  getUser: (): AuthUser | null => readJson<AuthUser>(USER_KEY),

  set: (token: string, user: AuthUser): void => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  clear: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(ORIGINAL_TOKEN_KEY);
    localStorage.removeItem(ORIGINAL_USER_KEY);
  },

  // ── Masquerade (superadmin → impersonate user) ─────────────────────────────
  getOriginalUser: (): AuthUser | null => readJson<AuthUser>(ORIGINAL_USER_KEY),

  isImpersonating: (): boolean => localStorage.getItem(ORIGINAL_TOKEN_KEY) !== null,

  startImpersonation: (newToken: string, newUser: AuthUser): void => {
    const currentToken = localStorage.getItem(TOKEN_KEY);
    const currentUser = localStorage.getItem(USER_KEY);
    if (!currentToken || !currentUser) {
      throw new Error('Cannot impersonate without an active session');
    }
    localStorage.setItem(ORIGINAL_TOKEN_KEY, currentToken);
    localStorage.setItem(ORIGINAL_USER_KEY, currentUser);
    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(USER_KEY, JSON.stringify(newUser));
  },

  exitImpersonation: (): void => {
    const origToken = localStorage.getItem(ORIGINAL_TOKEN_KEY);
    const origUser = localStorage.getItem(ORIGINAL_USER_KEY);
    if (!origToken || !origUser) return;
    localStorage.setItem(TOKEN_KEY, origToken);
    localStorage.setItem(USER_KEY, origUser);
    localStorage.removeItem(ORIGINAL_TOKEN_KEY);
    localStorage.removeItem(ORIGINAL_USER_KEY);
  },
};
