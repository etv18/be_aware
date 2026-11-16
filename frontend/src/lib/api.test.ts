import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiError, api, buildUrl } from './api';

const reply = (status: number, body?: unknown) => new Response(body === undefined ? null : JSON.stringify(body), { status });
const session = (token: string) => reply(200, { data: { csrf_token: token, authenticated: true, user: null, env_name: 'testing', env_label: 'TEST' } });

let fetchMock: ReturnType<typeof vi.fn>;
beforeEach(() => { fetchMock = vi.fn(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => vi.unstubAllGlobals());

describe('buildUrl', () => {
  it('adds the query and leaves out what is empty', () => {
    expect(buildUrl('/expenses', { q: 'pizza', start: '', end: undefined, year: 2026 })).toBe('/api/expenses?q=pizza&year=2026');
    expect(buildUrl('/expenses')).toBe('/api/expenses');
  });
});

describe('api', () => {
  it('reads JSON on success', async () => {
    fetchMock.mockResolvedValueOnce(reply(200, { data: [1], meta: { count: 1 } }));
    expect(await api.get('/expenses')).toEqual({ data: [1], meta: { count: 1 } });
  });

  it('sends the CSRF token and the JSON body on a write', async () => {
    fetchMock.mockResolvedValueOnce(session('tok-1')).mockResolvedValueOnce(reply(201, { data: { id: 1 } }));
    await api.post('/expenses', { amount: '1.00' });

    const [url, init] = fetchMock.mock.calls[1];
    expect(url).toBe('/api/expenses');
    expect(init.method).toBe('POST');
    expect(init.headers).toMatchObject({ 'X-CSRFToken': 'tok-1', 'Content-Type': 'application/json' });
    expect(init.body).toBe('{"amount":"1.00"}');
  });

  it('answers null to a 204', async () => {
    fetchMock.mockResolvedValueOnce(reply(204));
    expect(await api.delete('/expenses/1')).toBeNull();
  });

  it('turns an error answer into an ApiError with its fields', async () => {
    fetchMock.mockResolvedValueOnce(reply(422, { error: { code: 'validation_error', message: 'description: required', fields: { description: 'This field is required.' } } }));
    const error = await api.get('/expenses').catch((e) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 422, code: 'validation_error', fields: { description: 'This field is required.' } });
  });

  it('asks for a new token and tries once more when the token expired', async () => {
    fetchMock
      .mockResolvedValueOnce(reply(400, { error: { code: 'csrf_failed', message: 'expired' } }))
      .mockResolvedValueOnce(session('tok-2'))
      .mockResolvedValueOnce(reply(200, { data: 'ok' }));

    expect(await api.put('/expenses/1', {})).toEqual({ data: 'ok' });
    expect(fetchMock.mock.calls[2][1].headers).toMatchObject({ 'X-CSRFToken': 'tok-2' });
  });

  it('says so when the server cannot be reached', async () => {
    fetchMock.mockRejectedValueOnce(new TypeError('fetch failed'));
    expect(await api.get('/expenses').catch((e) => e)).toMatchObject({ status: 0, code: 'network_error' });
  });
});
