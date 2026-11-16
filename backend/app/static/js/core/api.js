// The only place that talks to the backend. Every call sends and receives JSON, to the endpoints of the controllers, and every failure
// becomes an ApiError with the same shape the server sends: {status, code, message, fields}.
// A React (or any other) frontend can reuse this file as it is.

const BASE = '';

export class ApiError extends Error {
  constructor(status, error = {}) {
    super(error.message || 'Something went wrong.');
    this.status = status;
    this.code = error.code || 'error';
    this.fields = error.fields || {};
  }
}

let csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || null;

async function getToken(force = false) {
  if (csrfToken && !force) return csrfToken;
  const response = await fetch(`/session`, { credentials: 'same-origin' });
  csrfToken = (await response.json()).data.csrf_token;
  return csrfToken;
}

function buildUrl(path, query) {
  const url = new URL(BASE + path, window.location.origin);
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') url.searchParams.set(key, value);
  });
  return url;
}

async function request(method, path, { query, body } = {}, retried = false) {
  const headers = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') headers['X-CSRFToken'] = await getToken();

  let response;
  try {
    response = await fetch(buildUrl(path, query), {
      method,
      headers,
      credentials: 'same-origin',
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, { code: 'network_error', message: 'Could not reach the server. Check your connection.' });
  }

  if (response.status === 204) return null;

  let payload = null;
  try { payload = await response.json(); } catch { /* not JSON */ }

  if (!response.ok) {
    const error = payload?.error || {};
    if (response.status === 401) {
      window.location.href = '/login';
    }
    if (error.code === 'csrf_failed' && !retried) {
      await getToken(true);
      return request(method, path, { query, body }, true);
    }
    throw new ApiError(response.status, error);
  }
  return payload;
}

export const api = {
  /** GET -> the whole payload: {data, meta?} */
  get: (path, query) => request('GET', path, { query }),
  post: (path, body) => request('POST', path, { body }),
  put: (path, body) => request('PUT', path, { body }),
  delete: (path) => request('DELETE', path),
};

/** GET and unwrap {data}. */
export const getData = async (path, query) => (await api.get(path, query)).data;

let optionsCache = null;
/** Banks, accounts, cards and categories for the selects. Cached until invalidateOptions(). */
export async function loadOptions() {
  if (!optionsCache) optionsCache = getData('/options');
  return optionsCache;
}
export const invalidateOptions = () => { optionsCache = null; };
