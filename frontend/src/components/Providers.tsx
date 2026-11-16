// The three things any page can ask for: the theme, a toast (the small message in the corner) and an "Are you sure?".
import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from 'react';

import { Dialog } from '@/components/Dialog';
import { Icon } from '@/components/Icon';
import { ApiError } from '@/lib/api';

// ------------------------------------------------------------------ theme
type Theme = 'light' | 'dark';
const ThemeContext = createContext<{ theme: Theme; toggle: () => void }>({ theme: 'light', toggle: () => {} });
export const useTheme = () => useContext(ThemeContext);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'); // index.html set it before the first paint

  const toggle = useCallback(() => {
    const next: Theme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch { /* private mode */ }
    setTheme(next);
  }, [theme]);

  const value = useMemo(() => ({ theme, toggle }), [theme, toggle]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

// ------------------------------------------------------------------ toasts
type ToastItem = { id: number; message: string; error: boolean };
type ToastApi = { toast: (message: string) => void; toastError: (error: unknown) => void };
const ToastContext = createContext<ToastApi>({ toast: () => {}, toastError: () => {} });
export const useToast = () => useContext(ToastContext);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const next = useRef(0);

  const show = useCallback((message: string, error: boolean) => {
    const id = ++next.current;
    setItems((current) => [...current, { id, message, error }]);
    setTimeout(() => setItems((current) => current.filter((item) => item.id !== id)), error ? 6000 : 3200);
  }, []);

  const api = useMemo<ToastApi>(() => ({
    toast: (message) => show(message, false),
    toastError: (error) => show(error instanceof ApiError || error instanceof Error ? error.message : 'Something went wrong.', true),
  }), [show]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div aria-live="polite" className="pointer-events-none fixed inset-x-4 bottom-4 z-[60] flex flex-col items-center gap-2 sm:inset-x-auto sm:right-4 sm:items-end">
        {items.map((item) => (
          <div key={item.id} className="pointer-events-auto flex max-w-sm items-start gap-2.5 rounded-lg border border-line bg-surface px-3.5 py-2.5 text-sm shadow-lg">
            <span className={`mt-0.5 ${item.error ? 'text-negative' : 'text-positive'}`}><Icon name={item.error ? 'circle-alert' : 'circle-check'} /></span>
            <span>{item.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

// ------------------------------------------------------------------ "Are you sure?"
type Ask = { title: string; text?: string };
const ConfirmContext = createContext<(ask: Ask) => Promise<boolean>>(async () => false);

/** const confirm = useConfirm();   if (await confirm({ title: 'Delete this expense?', text: '...' })) ... */
export const useConfirm = () => useContext(ConfirmContext);

export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [ask, setAsk] = useState<Ask | null>(null);
  const answer = useRef<(yes: boolean) => void>(() => {});

  const confirm = useCallback((question: Ask) => new Promise<boolean>((resolve) => {
    answer.current = resolve;
    setAsk(question);
  }), []);

  const finish = (yes: boolean) => {
    answer.current(yes);
    setAsk(null);
  };

  return (
    <ConfirmContext.Provider value={confirm}>
      {children}
      <Dialog open={ask !== null} onClose={() => finish(false)}>
        <div className="p-5">
          <h2 className="text-base font-semibold">{ask?.title ?? 'Are you sure?'}</h2>
          <p className="mt-1.5 text-sm text-muted">{ask?.text}</p>
          <div className="mt-5 flex justify-end gap-2">
            <button type="button" className="btn btn-outline" onClick={() => finish(false)}>Cancel</button>
            <button type="button" className="btn btn-danger" onClick={() => finish(true)}>Delete</button>
          </div>
        </div>
      </Dialog>
    </ConfirmContext.Provider>
  );
}
