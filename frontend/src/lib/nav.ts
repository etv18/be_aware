// The menu. `key` picks the module color (--m-<key> in app.css); `path` is the page.
// MIGRATED lists the pages that already exist in React: their links stay inside the React app, the others still
// go to the Jinja page of the same URL. Add a key here when a page is ported; when the list is complete, delete it.
import type { IconName } from '@/components/Icon';

export type NavItem = { key: string; path: string; icon: IconName; label: string };
export type NavGroup = { name: string; icon: IconName; items: NavItem[] };

export const GROUPS: NavGroup[] = [
  { name: 'Home', icon: 'house', items: [{ key: 'home', path: '/', icon: 'house', label: 'Home' }] },
  {
    name: 'Cash flow', icon: 'arrow-left-right', items: [
      { key: 'incomes', path: '/incomes', icon: 'trending-up', label: 'Incomes' },
      { key: 'expenses', path: '/expenses', icon: 'receipt', label: 'Expenses' },
      { key: 'categories', path: '/expense_categories', icon: 'tags', label: 'Expense categories' },
    ],
  },
  {
    name: 'Bank products', icon: 'wallet-cards', items: [
      { key: 'banks', path: '/banks', icon: 'landmark', label: 'Banks' },
      { key: 'accounts', path: '/bank_accounts', icon: 'wallet', label: 'Bank accounts' },
      { key: 'cards', path: '/credit_cards', icon: 'credit-card', label: 'Credit cards' },
    ],
  },
  {
    name: 'Cash', icon: 'banknote', items: [
      { key: 'withdrawals', path: '/withdrawals', icon: 'arrow-up-from-line', label: 'Withdrawals' },
      { key: 'deposits', path: '/deposits', icon: 'arrow-down-to-line', label: 'Deposits' },
      { key: 'cash', path: '/cash_ledger', icon: 'coins', label: 'Cash ledger' },
    ],
  },
  {
    name: 'Lending', icon: 'handshake', items: [
      { key: 'loans', path: '/loans', icon: 'hand-coins', label: 'Loans' },
      { key: 'debts', path: '/debts', icon: 'scroll-text', label: 'Debts' },
    ],
  },
];

export const MIGRATED = new Set(['expenses']);

/** Which menu entry a URL belongs to ('/loans/12' -> loans). */
export function currentItem(pathname: string): { item: NavItem | null; group: NavGroup | null } {
  const first = `/${pathname.split('/')[1] ?? ''}`;
  for (const group of GROUPS) {
    const item = group.items.find((candidate) => candidate.path === first);
    if (item) return { item, group };
  }
  return { item: null, group: null };
}
