// The records of one account / card / category, one tab per kind. (partials/ui.html records_tabs + static/js/records.js)
// Each kind says which columns it shows. A cell is text, so nothing a person typed can run as HTML.
import { useMemo, useState } from 'react';

import { Icon } from '@/components/Icon';
import { FilterBar, RowActions } from '@/components/ui/table';
import { filterRows, formatDate, money, source, sum } from '@/lib/format';
import type { Filters } from '@/lib/queries';
import type { RecordsKinds } from '@/types';

type Row = Record<string, any>; // the kinds have different fields; each column knows what it reads

type Column = {
  label: string;
  text: (row: Row) => string;
  right?: boolean;
  className?: string | ((row: Row) => string);
  sub?: (row: Row) => string | null | undefined; // a second, smaller line under the text
};

const column = (label: string, text: Column['text'], options: Partial<Column> = {}): Column => ({ label, text, ...options });

const date = column('Date', (r) => formatDate(r.created_at), { className: 'whitespace-nowrap text-muted' });
const amount = (tone = '') => column('Amount', (r) => money(r.amount), { right: true, className: `font-medium ${tone}` });
const person = column('Person', (r) => r.person_name || '–', { sub: (r) => r.description });
const description = column('Description', (r) => r.description || '–');

// loans and debts share their columns; only the "where the money went" label and the open status change
const obligation = (sourceLabel: string, openLabel: string, openClass: string): Column[] => [
  person,
  column('Status', (r) => (r.is_active ? openLabel : 'Paid'), { className: (r) => (r.is_active ? openClass : 'text-positive font-bold') }),
  column(sourceLabel, source),
  date,
  column('Paid', (r) => money(r.total_paid), { right: true }),
  column('Remaining', (r) => money(r.remaining_amount), { right: true }),
  amount(),
];

const KINDS: Record<keyof RecordsKinds, [string, Column[]]> = {
  expenses: ['Expenses', [description, column('Category', (r) => r.expense_category_name || '–'), column('Paid with', source), date, amount('text-negative')]],
  incomes: ['Incomes', [description, column('Received in', source), date, amount('text-positive')]],
  deposits: ['Deposits', [description, column('Into account', (r) => r.bank_account_name || '–'), date, amount()]],
  withdrawals: ['Withdrawals', [description, column('From account', (r) => r.bank_account_name || '–'), date, amount()]],
  loans: ['Loans', obligation('Lent from', 'COLLECT', 'text-yellow-400 font-black')],
  loan_payments: ['Loan payments', [person, column('Received in', source), date, amount('text-positive')]],
  debts: ['Debts', obligation('Received in', 'ACTIVE', 'text-negative font-black')],
  debt_payments: ['Debt payments', [person, column('Paid from', source), date, amount('text-negative')]],
  credit_card_payments: ['Card payments', [column('Card', (r) => r.credit_card_name || '–'), column('Paid from', (r) => (r.is_cashback ? 'Cashback' : r.bank_account_name || '–')), date, amount('text-positive')]],
  bank_transfers: ['Transfers', [column('Code', (r) => r.code ?? '', { className: 'font-mono text-xs' }), column('From', (r) => r.from_bank_account_name || '–'), column('To', (r) => r.to_bank_account_name || '–'), date, amount()]],
};

const classOf = (value: Column['className'], row: Row) => (typeof value === 'function' ? value(row) : value) ?? '';

export function RecordsTabs({ records, bankProduct }: { records: RecordsKinds, bankProduct: string }) {
  const kinds = (Object.keys(KINDS) as (keyof RecordsKinds)[]).filter((kind) => records[kind]?.length);
  const [picked, setPicked] = useState<keyof RecordsKinds | null>(null);
  const [filters, setFilters] = useState<Filters>({});
  const current = picked && kinds.includes(picked) ? picked : kinds[0];

  const rows = useMemo<Row[]>(() => (current ? filterRows((records[current] ?? []) as Row[], filters) : []), [records, current, filters]);
  const filtering = Boolean(filters.q || (filters.start && filters.end));

  if (!current) { // nothing at all: only the "No records yet" message
    return (
      <section className="card overflow-hidden">
        <div className="flex flex-col items-center px-6 py-14 text-center">
          <span className="mb-3 flex size-10 items-center justify-center rounded-full bg-sunken text-muted"><Icon name="inbox" /></span>
          <p className="text-sm font-medium">No records yet</p>
          <p className="mt-1 max-w-sm text-sm text-muted">Everything that moves through here will be listed.</p>
        </div>
      </section>
    );
  }

  const columns = KINDS[current][1];
  return (
    <div>
      <div className="mb-3 scroll-x">
        <div className="tabs" role="tablist">
          {kinds.map((kind) => (
            <button key={kind} type="button" role="tab" aria-selected={kind === current} onClick={() => setPicked(kind)}>
              {KINDS[kind][0]} <span className="text-faint">{records[kind]?.length}</span>
            </button>
          ))}
        </div>
      </div>
      <section className="card overflow-hidden">
        <FilterBar placeholder="Search description or amount…" onChange={setFilters} />
        <div className="table-wrap table-scroll">
          <table className="table">
            <thead>
              <tr>
                {columns.map((c) => <th key={c.label} className={c.right ? 'text-right' : ''}>{c.label}</th>)}
                {/* If credit card tab is selected show this column */}
                {current.toLowerCase() === 'credit_card_payments'  &&
                 bankProduct === 'credit_card'&& (
                    <th className='text-right'>Action</th>
                )}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  {columns.map((c) => (
                    <td key={c.label} className={`${c.right ? 'num text-right' : ''} ${classOf(c.className, row)}`}>
                      <span className={c.sub ? 'block font-medium' : ''}>{c.text(row)}</span>
                      {c.sub?.(row) ? <span className="block max-w-[28ch] truncate text-xs text-muted">{c.sub(row)}</span> : null}
                    </td>
                  ))}
                  {/* If credit card tab is selected show this button */}
                  {current.toLowerCase() === 'credit_card_payments' && 
                    bankProduct === 'credit_card' &&
                  (
                    <RowActions onDelete={() => {}} />
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {rows.length === 0 && (
          <div className="flex flex-col items-center px-6 py-14 text-center">
            <span className="mb-3 flex size-10 items-center justify-center rounded-full bg-sunken text-muted"><Icon name="inbox" /></span>
            <p className="text-sm font-medium">Nothing matches</p>
            <p className="mt-1 max-w-sm text-sm text-muted">Try other words, another amount or another date range.</p>
          </div>
        )}
        <div className="flex items-center justify-between gap-3 border-t border-line bg-sunken/40 px-4 py-2.5 text-sm">
          <span className="text-muted">{filtering ? 'Filtered total' : 'Total'} · {rows.length} {rows.length === 1 ? 'record' : 'records'}</span>
          <span className="num font-semibold">{money(sum(rows.map((r) => r.amount)))}</span>
        </div>
      </section>
    </div>
  );
}

