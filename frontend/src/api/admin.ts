/** Admin CRUD: companies + users + impersonate. */
import { apiRequest } from './client';
import type { LoginResponse } from './auth';

export type Role = 'superadmin' | 'admin' | 'user';

export interface Company {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreate {
  name: string;
}

export interface CompanyUpdate {
  name?: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: Role;
  company_id: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  role: Role;
  full_name?: string | null;
  company_id?: string;
}

export interface UserUpdate {
  email?: string;
  password?: string;
  role?: Role;
  full_name?: string | null;
}

export const adminApi = {
  // Companies
  listCompanies: () => apiRequest<Company[]>('/admin/companies/'),
  createCompany: (data: CompanyCreate) =>
    apiRequest<Company>('/admin/companies/', { method: 'POST', body: data }),
  updateCompany: (id: string, data: CompanyUpdate) =>
    apiRequest<Company>(`/admin/companies/${id}/`, { method: 'PATCH', body: data }),
  deleteCompany: (id: string) =>
    apiRequest<void>(`/admin/companies/${id}/`, { method: 'DELETE' }),

  // Users
  listUsers: (companyId?: string) =>
    apiRequest<User[]>(
      `/admin/users/${companyId ? `?company_id=${encodeURIComponent(companyId)}` : ''}`,
    ),
  createUser: (data: UserCreate) =>
    apiRequest<User>('/admin/users/', { method: 'POST', body: data }),
  updateUser: (id: string, data: UserUpdate) =>
    apiRequest<User>(`/admin/users/${id}/`, { method: 'PATCH', body: data }),
  deleteUser: (id: string) =>
    apiRequest<void>(`/admin/users/${id}/`, { method: 'DELETE' }),

  // Impersonate — returns LoginResponse-shape (token + identity)
  impersonate: (userId: string) =>
    apiRequest<LoginResponse>(`/admin/users/${userId}/impersonate/`, { method: 'POST' }),
};
