// Every request to the server goes through here: JSON in, JSON out, the CSRF token on writes, and one kind of error.
//   const { data, meta } = await api.get<List<Expense>>('/expenses', { q: 'pizza' });   // GET /api/expenses?q=pizza
import type { Session } from '@/types';

const API = '/api';

export class ApiError extends Error {
  status: number;
  code: string;
  fields: Record<string, string>; // {field_name: 'message'} for a form

  constructor(status: number, error: { code?: string; message?: string; fields?: Record<string, string> } = {}) {
    super(error.message || 'Something went wrong.');
    this.status = status;
    this.code = error.code || 'error';
    this.fields = error.fields || {};
  }
}

let csrf: string | null = null;

/** The token that has to come back in X-CSRFToken on POST, PUT and DELETE. */
async function csrfToken(force = false): Promise<string> {
  if (!csrf || force) csrf = (await fetchSession()).data.csrf_token;
  return csrf;
}

/** GET /api/session: who is logged in, the CSRF token and the environment badge. Also remembers the token. */
export async function fetchSession(): Promise<{ data: Session }> {
  const response = await fetch(`${API}/session`, { credentials: 'same-origin', headers: { Accept: 'application/json' } });
  const payload = await response.json();
  csrf = payload.data.csrf_token;
  return payload;
}

type Query = Record<string, string | number | null | undefined>;

export function buildUrl(path: string, query: Query = {}): string {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') params.set(key, String(value));
  });
  const text = params.toString();
  return `${API}${path}${text ? `?${text}` : ''}`;
}

async function request<T>(method: string, path: string, { query, body }: { query?: Query; body?: unknown } = {}, retried = false): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') headers['X-CSRFToken'] = await csrfToken();

  let response: Response;
  try {
    response = await fetch(buildUrl(path, query), {
      method, headers, credentials: 'same-origin', body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, { code: 'network_error', message: 'Could not reach the server. Check your connection.' });
  }
  if (response.status === 204) return null as T;

  let payload: any = null;
  try { payload = await response.json(); } catch { /* not JSON */ }

  if (!response.ok) {
    const error = payload?.error || {};
    if (error.code === 'csrf_failed' && !retried) { // the token expired: get a new one and try once more
      await csrfToken(true);
      return request<T>(method, path, { query, body }, true);
    }
    throw new ApiError(response.status, error);
  }
  return payload as T;
}

export const api = {
  get: <T>(path: string, query?: Query) => request<T>('GET', path, { query }),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, { body }),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, { body }),
  delete: (path: string) => request<null>('DELETE', path),
};
