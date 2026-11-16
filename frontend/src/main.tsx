import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { Layout } from '@/components/Layout';
import { ConfirmProvider, ThemeProvider, ToastProvider } from '@/components/Providers';
import { RequireAuth } from '@/components/RequireAuth';
import { ApiError } from '@/lib/api';
import { Expenses } from '@/pages/Expenses';
import { Login } from '@/pages/Login';
import { NotFound } from '@/pages/NotFound';

import './app.css';

// Any answer of 401 (the session ended): ask who is logged in again, and RequireAuth sends the person to the login form.
const sessionEnded = (error: unknown) => {
  if (error instanceof ApiError && error.status === 401) client.invalidateQueries({ queryKey: ['session'] });
};

const client: QueryClient = new QueryClient({
  queryCache: new QueryCache({ onError: sessionEnded }),
  mutationCache: new MutationCache({ onError: sessionEnded }),
  defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
});

// While the Jinja pages still exist the app lives under /app (see app/routes/spa_routes.py); `npm run dev` serves it at /.
const basename = import.meta.env.VITE_BASENAME ?? (import.meta.env.DEV ? '/' : '/app');

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={client}>
      <ThemeProvider>
        <ToastProvider>
          <ConfirmProvider>
            <BrowserRouter basename={basename}>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route element={<RequireAuth />}>
                  <Route element={<Layout />}>
                    <Route path="/" element={<Navigate to="/expenses" replace />} />
                    <Route path="/expenses" element={<Expenses />} />
                    <Route path="*" element={<NotFound />} />
                  </Route>
                </Route>
              </Routes>
            </BrowserRouter>
          </ConfirmProvider>
        </ToastProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
);
