import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { Layout } from '@/components/Layout';
import { ConfirmProvider, ThemeProvider, ToastProvider } from '@/components/Providers';
import { RequireAuth } from '@/components/RequireAuth';
import { ApiError } from '@/lib/api';
import { BankAccounts } from '@/pages/BankAccounts';
import { Banks } from '@/pages/Banks';
import { Deposits, Withdrawals } from '@/pages/CashMovements';
import { CreditCards } from '@/pages/CreditCards';
import { BankAccountDetail, CreditCardDetail, ExpenseCategoryDetail } from '@/pages/Details';
import { ExpenseCategories } from '@/pages/ExpenseCategories';
import { Expenses } from '@/pages/Expenses';
import { Home } from '@/pages/Home';
import { Incomes } from '@/pages/Incomes';
import { BankLedger, CardLedger, CashLedger } from '@/pages/Ledgers';
import { DebtDetail, LoanDetail } from '@/pages/ObligationDetail';
import { Debts, Loans } from '@/pages/Obligations';
import { DebtPayments, LoanPayments } from '@/pages/PaymentLists';
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

// The app lives at "/" (Flask answers every page URL with index.html, see backend/app/routes/spa_routes.py).
const basename = '/';

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
                    <Route path="/" element={<Home />} />
                    <Route path="/expenses" element={<Expenses />} />
                    <Route path="/incomes" element={<Incomes />} />
                    <Route path="/withdrawals" element={<Withdrawals />} />
                    <Route path="/deposits" element={<Deposits />} />
                    <Route path="/expense_categories" element={<ExpenseCategories />} />
                    <Route path="/expense_categories/:id" element={<ExpenseCategoryDetail />} />
                    <Route path="/banks" element={<Banks />} />
                    <Route path="/bank_accounts" element={<BankAccounts />} />
                    <Route path="/bank_accounts/:id" element={<BankAccountDetail />} />
                    <Route path="/credit_cards" element={<CreditCards />} />
                    <Route path="/credit_cards/:id" element={<CreditCardDetail />} />
                    <Route path="/cash_ledger" element={<CashLedger />} />
                    <Route path="/bank_ledger" element={<BankLedger />} />
                    <Route path="/card_ledger" element={<CardLedger />} />
                    <Route path="/loans" element={<Loans />} />
                    <Route path="/loans/:id" element={<LoanDetail />} />
                    <Route path="/loan_payments" element={<LoanPayments />} />
                    <Route path="/debts" element={<Debts />} />
                    <Route path="/debts/:id" element={<DebtDetail />} />
                    <Route path="/debt_payments" element={<DebtPayments />} />
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
