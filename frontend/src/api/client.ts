/**
 * Centralized fetch wrapper.
 *
 * - Prepends /api/v1 (calls pass the relative path, e.g. "/auth/login")
 * - Injects Bearer token automatically
 * - Throws ApiError with status + parsed body on non-2xx
 * - Handles 401 → clears auth + emits an event so the router can redirect
 */
import { authStorage } from '../auth/storage';

const BASE_URL = '/api/v1';

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  signal?: AbortSignal;
}

export async function apiRequest<T = unknown>(
  path: string,
  opts: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  const token = authStorage.getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method: opts.method ?? 'GET',
    headers,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    signal: opts.signal,
  });

  if (res.status === 401) {
    authStorage.clear();
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
  }

  let body: unknown = null;
  const ct = res.headers.get('content-type') ?? '';
  if (ct.includes('application/json')) {
    body = await res.json().catch(() => null);
  } else {
    body = await res.text().catch(() => null);
  }

  if (!res.ok) {
    const detail =
      (body && typeof body === 'object' && 'detail' in body
        ? String((body as { detail: unknown }).detail)
        : null) ?? `HTTP ${res.status}`;
    throw new ApiError(detail, res.status, body);
  }

  return body as T;
}
