// The login form. (templates/auth/login.html)
import { useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';

import { Icon } from '@/components/Icon';
import { ApiError, api } from '@/lib/api';
import { useSession, usePageTitle } from '@/lib/queries';

export function Login() {
  usePageTitle('Log in');
  const client = useQueryClient();
  const navigate = useNavigate();
  const from = (useLocation().state as { from?: string } | null)?.from;
  const session = useSession();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (session.data?.data.authenticated) return <Navigate to={from ?? '/expenses'} replace />; // '/' once Home is ported

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      await api.post('/login', { username, password });
      await client.invalidateQueries({ queryKey: ['session'] });
      navigate(from ?? '/expenses', { replace: true });
    } catch (caught) {
      setError(caught instanceof ApiError ? (caught.status === 429 ? 'Too many attempts. Try again in a little while.' : caught.message) : 'Could not log in.');
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <main className="w-full max-w-sm">
        <div className="mb-6 flex items-center gap-3">
          <span className="flex size-10 items-center justify-center rounded-xl bg-ink text-ink-inverse"><Icon name="eye" className="size-5" /></span>
          <div>
            <h1 className="text-lg font-semibold leading-tight">Be Aware</h1>
            <p className="text-sm text-muted">Log in to see your money.</p>
          </div>
        </div>

        <form className="card card-pad space-y-4" onSubmit={submit}>
          {error && <p className="rounded-lg border border-negative/30 bg-negative/10 px-3 py-2 text-sm text-negative" role="alert">{error}</p>}
          <div>
            <label className="label" htmlFor="username">Username</label>
            <input className="input" id="username" type="text" autoComplete="username" autoFocus required value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div>
            <label className="label" htmlFor="password">Password</label>
            <input className="input" id="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-primary w-full" disabled={busy}>Log in</button>
        </form>
      </main>
    </div>
  );
}
