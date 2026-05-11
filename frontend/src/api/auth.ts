/** Auth API surface. */
import { apiRequest } from './client';
import type { AuthUser } from '../auth/storage';

export interface LoginResponse extends AuthUser {
  token: string;
}

export const authApi = {
  login: (email: string, password: string) =>
    apiRequest<LoginResponse>('/auth/login/', {
      method: 'POST',
      body: { email, password },
    }),

  me: () => apiRequest<AuthUser & { id: string }>('/auth/me/'),
};
