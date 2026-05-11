/**
 * JWT + identity cache in localStorage.
 *
 * Single point of mutation — every read/write of auth state goes through here.
 * If we ever switch storage strategy (cookie, sessionStorage), only this file changes.
 */
const TOKEN_KEY = 'wm_token';
const USER_KEY = 'wm_user';

export interface AuthUser {
  user_id: string;
  email: string;
  full_name: string | null;
  role: 'superadmin' | 'admin' | 'user';
  company_id: string;
  company_name: string;
}

export const authStorage = {
  getToken: (): string | null => localStorage.getItem(TOKEN_KEY),

  getUser: (): AuthUser | null => {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as AuthUser;
    } catch {
      return null;
    }
  },

  set: (token: string, user: AuthUser): void => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  clear: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};
